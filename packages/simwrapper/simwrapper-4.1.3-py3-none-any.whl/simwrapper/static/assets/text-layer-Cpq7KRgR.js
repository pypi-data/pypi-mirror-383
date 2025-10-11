import{w as F,E as Ce,p as Pe,F as Le,H as be,I as de,x as B,y as U,U as w,B as D,G as N,q as A}from"./layer-GQvgsG1_.js";const Se="compositeLayer.renderLayers";class ue extends F{get isComposite(){return!0}get isDrawable(){return!1}get isLoaded(){return super.isLoaded&&this.getSubLayers().every(e=>e.isLoaded)}getSubLayers(){return this.internalState&&this.internalState.subLayers||[]}initializeState(e){}setState(e){super.setState(e),this.setNeedsUpdate()}getPickingInfo({info:e}){const{object:t}=e;return t&&t.__source&&t.__source.parent&&t.__source.parent.id===this.id&&(e.object=t.__source.object,e.index=t.__source.index),e}filterSubLayer(e){return!0}shouldRenderSubLayer(e,t){return t&&t.length}getSubLayerClass(e,t){const{_subLayerProps:i}=this.props;return i&&i[e]&&i[e].type||t}getSubLayerRow(e,t,i){return e.__source={parent:this,object:t,index:i},e}getSubLayerAccessor(e){if(typeof e=="function"){const t={index:-1,data:this.props.data,target:[]};return(i,s)=>i&&i.__source?(t.index=i.__source.index,e(i.__source.object,t)):e(i,s)}return e}getSubLayerProps(e={}){const{opacity:t,pickable:i,visible:s,parameters:o,getPolygonOffset:a,highlightedObjectIndex:n,autoHighlight:r,highlightColor:l,coordinateSystem:d,coordinateOrigin:u,wrapLongitude:g,positionFormat:f,modelMatrix:p,extensions:x,fetch:h,operation:v,_subLayerProps:P}=this.props,m={id:"",updateTriggers:{},opacity:t,pickable:i,visible:s,parameters:o,getPolygonOffset:a,highlightedObjectIndex:n,autoHighlight:r,highlightColor:l,coordinateSystem:d,coordinateOrigin:u,wrapLongitude:g,positionFormat:f,modelMatrix:p,extensions:x,fetch:h,operation:v},L=P&&e.id&&P[e.id],_=L&&L.updateTriggers,y=e.id||"sublayer";if(L){const M=this.props[Ce],b=e.type?e.type._propTypes:{};for(const S in L){const E=b[S]||M[S];E&&E.type==="accessor"&&(L[S]=this.getSubLayerAccessor(L[S]))}}Object.assign(m,e,L),m.id=`${this.props.id}-${y}`,m.updateTriggers={all:this.props.updateTriggers?.all,...e.updateTriggers,..._};for(const M of x){const b=M.getSubLayerProps.call(this,M);b&&Object.assign(m,b,{updateTriggers:Object.assign(m.updateTriggers,b.updateTriggers)})}return m}_updateAutoHighlight(e){for(const t of this.getSubLayers())t.updateAutoHighlight(e)}_getAttributeManager(){return null}_postUpdate(e,t){let i=this.internalState.subLayers;const s=!i||this.needsUpdate();if(s){const o=this.renderLayers();i=Pe(o,Boolean),this.internalState.subLayers=i}Le(Se,this,s,i);for(const o of i)o.parent=this}}ue.layerName="CompositeLayer";const V=`uniform iconUniforms {
  float sizeScale;
  vec2 iconsTextureDim;
  float sizeMinPixels;
  float sizeMaxPixels;
  bool billboard;
  highp int sizeUnits;
  float alphaCutoff;
} icon;
`,Te={name:"icon",vs:V,fs:V,uniformTypes:{sizeScale:"f32",iconsTextureDim:"vec2<f32>",sizeMinPixels:"f32",sizeMaxPixels:"f32",billboard:"f32",sizeUnits:"i32",alphaCutoff:"f32"}},Me=`#version 300 es
#define SHADER_NAME icon-layer-vertex-shader
in vec2 positions;
in vec3 instancePositions;
in vec3 instancePositions64Low;
in float instanceSizes;
in float instanceAngles;
in vec4 instanceColors;
in vec3 instancePickingColors;
in vec4 instanceIconFrames;
in float instanceColorModes;
in vec2 instanceOffsets;
in vec2 instancePixelOffset;
out float vColorMode;
out vec4 vColor;
out vec2 vTextureCoords;
out vec2 uv;
vec2 rotate_by_angle(vec2 vertex, float angle) {
float angle_radian = angle * PI / 180.0;
float cos_angle = cos(angle_radian);
float sin_angle = sin(angle_radian);
mat2 rotationMatrix = mat2(cos_angle, -sin_angle, sin_angle, cos_angle);
return rotationMatrix * vertex;
}
void main(void) {
geometry.worldPosition = instancePositions;
geometry.uv = positions;
geometry.pickingColor = instancePickingColors;
uv = positions;
vec2 iconSize = instanceIconFrames.zw;
float sizePixels = clamp(
project_size_to_pixel(instanceSizes * icon.sizeScale, icon.sizeUnits),
icon.sizeMinPixels, icon.sizeMaxPixels
);
float instanceScale = iconSize.y == 0.0 ? 0.0 : sizePixels / iconSize.y;
vec2 pixelOffset = positions / 2.0 * iconSize + instanceOffsets;
pixelOffset = rotate_by_angle(pixelOffset, instanceAngles) * instanceScale;
pixelOffset += instancePixelOffset;
pixelOffset.y *= -1.0;
if (icon.billboard)  {
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, vec3(0.0), geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
vec3 offset = vec3(pixelOffset, 0.0);
DECKGL_FILTER_SIZE(offset, geometry);
gl_Position.xy += project_pixel_size_to_clipspace(offset.xy);
} else {
vec3 offset_common = vec3(project_pixel_size(pixelOffset), 0.0);
DECKGL_FILTER_SIZE(offset_common, geometry);
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, offset_common, geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
}
vTextureCoords = mix(
instanceIconFrames.xy,
instanceIconFrames.xy + iconSize,
(positions.xy + 1.0) / 2.0
) / icon.iconsTextureDim;
vColor = instanceColors;
DECKGL_FILTER_COLOR(vColor, geometry);
vColorMode = instanceColorModes;
}
`,Ie=`#version 300 es
#define SHADER_NAME icon-layer-fragment-shader
precision highp float;
uniform sampler2D iconsTexture;
in float vColorMode;
in vec4 vColor;
in vec2 vTextureCoords;
in vec2 uv;
out vec4 fragColor;
void main(void) {
geometry.uv = uv;
vec4 texColor = texture(iconsTexture, vTextureCoords);
vec3 color = mix(texColor.rgb, vColor.rgb, vColorMode);
float a = texColor.a * layer.opacity * vColor.a;
if (a < icon.alphaCutoff) {
discard;
}
fragColor = vec4(color, a);
DECKGL_FILTER_COLOR(fragColor, geometry);
}
`,Ee=1024,ze=4,q=()=>{},Y={minFilter:"linear",mipmapFilter:"linear",magFilter:"linear",addressModeU:"clamp-to-edge",addressModeV:"clamp-to-edge"},Re={x:0,y:0,width:0,height:0};function Ae(c){return Math.pow(2,Math.ceil(Math.log2(c)))}function we(c,e,t,i){const s=Math.min(t/e.width,i/e.height),o=Math.floor(e.width*s),a=Math.floor(e.height*s);return s===1?{image:e,width:o,height:a}:(c.canvas.height=a,c.canvas.width=o,c.clearRect(0,0,o,a),c.drawImage(e,0,0,e.width,e.height,0,0,o,a),{image:c.canvas,width:o,height:a})}function R(c){return c&&(c.id||c.url)}function Oe(c,e,t,i){const{width:s,height:o,device:a}=c,n=a.createTexture({format:"rgba8unorm",width:e,height:t,sampler:i,mipmaps:!0}),r=a.createCommandEncoder();return r.copyTextureToTexture({sourceTexture:c,destinationTexture:n,width:s,height:o}),r.finish(),c.destroy(),n}function X(c,e,t){for(let i=0;i<e.length;i++){const{icon:s,xOffset:o}=e[i],a=R(s);c[a]={...s,x:o,y:t}}}function Fe({icons:c,buffer:e,mapping:t={},xOffset:i=0,yOffset:s=0,rowHeight:o=0,canvasWidth:a}){let n=[];for(let r=0;r<c.length;r++){const l=c[r],d=R(l);if(!t[d]){const{height:u,width:g}=l;i+g+e>a&&(X(t,n,s),i=0,s=o+s+e,o=0,n=[]),n.push({icon:l,xOffset:i}),i=i+g+e,o=Math.max(o,u)}}return n.length>0&&X(t,n,s),{mapping:t,rowHeight:o,xOffset:i,yOffset:s,canvasWidth:a,canvasHeight:Ae(o+s+e)}}function ke(c,e,t){if(!c||!e)return null;t=t||{};const i={},{iterable:s,objectInfo:o}=de(c);for(const a of s){o.index++;const n=e(a,o),r=R(n);if(!n)throw new Error("Icon is missing.");if(!n.url)throw new Error("Icon url is missing.");!i[r]&&(!t[r]||n.url!==t[r].url)&&(i[r]={...n,source:a,sourceIndex:o.index})}return i}class We{constructor(e,{onUpdate:t=q,onError:i=q}){this._loadOptions=null,this._texture=null,this._externalTexture=null,this._mapping={},this._samplerParameters=null,this._pendingCount=0,this._autoPacking=!1,this._xOffset=0,this._yOffset=0,this._rowHeight=0,this._buffer=ze,this._canvasWidth=Ee,this._canvasHeight=0,this._canvas=null,this.device=e,this.onUpdate=t,this.onError=i}finalize(){this._texture?.delete()}getTexture(){return this._texture||this._externalTexture}getIconMapping(e){const t=this._autoPacking?R(e):e;return this._mapping[t]||Re}setProps({loadOptions:e,autoPacking:t,iconAtlas:i,iconMapping:s,textureParameters:o}){e&&(this._loadOptions=e),t!==void 0&&(this._autoPacking=t),s&&(this._mapping=s),i&&(this._texture?.delete(),this._texture=null,this._externalTexture=i),o&&(this._samplerParameters=o)}get isLoaded(){return this._pendingCount===0}packIcons(e,t){if(!this._autoPacking||typeof document>"u")return;const i=Object.values(ke(e,t,this._mapping)||{});if(i.length>0){const{mapping:s,xOffset:o,yOffset:a,rowHeight:n,canvasHeight:r}=Fe({icons:i,buffer:this._buffer,canvasWidth:this._canvasWidth,mapping:this._mapping,rowHeight:this._rowHeight,xOffset:this._xOffset,yOffset:this._yOffset});this._rowHeight=n,this._mapping=s,this._xOffset=o,this._yOffset=a,this._canvasHeight=r,this._texture||(this._texture=this.device.createTexture({format:"rgba8unorm",width:this._canvasWidth,height:this._canvasHeight,sampler:this._samplerParameters||Y,mipmaps:!0})),this._texture.height!==this._canvasHeight&&(this._texture=Oe(this._texture,this._canvasWidth,this._canvasHeight,this._samplerParameters||Y)),this.onUpdate(),this._canvas=this._canvas||document.createElement("canvas"),this._loadIcons(i)}}_loadIcons(e){const t=this._canvas.getContext("2d",{willReadFrequently:!0});for(const i of e)this._pendingCount++,be(i.url,this._loadOptions).then(s=>{const o=R(i),a=this._mapping[o],{x:n,y:r,width:l,height:d}=a,{image:u,width:g,height:f}=we(t,s,l,d);this._texture?.copyExternalImage({image:u,x:n+(l-g)/2,y:r+(d-f)/2,width:g,height:f}),a.width=g,a.height=f,this._texture.generateMipmap(),this.onUpdate()}).catch(s=>{this.onError({url:i.url,source:i.source,sourceIndex:i.sourceIndex,loadOptions:this._loadOptions,error:s})}).finally(()=>{this._pendingCount--})}}const ge=[0,0,0,255],Be={iconAtlas:{type:"image",value:null,async:!0},iconMapping:{type:"object",value:{},async:!0},sizeScale:{type:"number",value:1,min:0},billboard:!0,sizeUnits:"pixels",sizeMinPixels:{type:"number",min:0,value:0},sizeMaxPixels:{type:"number",min:0,value:Number.MAX_SAFE_INTEGER},alphaCutoff:{type:"number",value:.05,min:0,max:1},getPosition:{type:"accessor",value:c=>c.position},getIcon:{type:"accessor",value:c=>c.icon},getColor:{type:"accessor",value:ge},getSize:{type:"accessor",value:1},getAngle:{type:"accessor",value:0},getPixelOffset:{type:"accessor",value:[0,0]},onIconError:{type:"function",value:null,optional:!0},textureParameters:{type:"object",ignore:!0,value:null}};class G extends F{getShaders(){return super.getShaders({vs:Me,fs:Ie,modules:[B,U,Te]})}initializeState(){this.state={iconManager:new We(this.context.device,{onUpdate:this._onUpdate.bind(this),onError:this._onError.bind(this)})},this.getAttributeManager().addInstanced({instancePositions:{size:3,type:"float64",fp64:this.use64bitPositions(),transition:!0,accessor:"getPosition"},instanceSizes:{size:1,transition:!0,accessor:"getSize",defaultValue:1},instanceOffsets:{size:2,accessor:"getIcon",transform:this.getInstanceOffset},instanceIconFrames:{size:4,accessor:"getIcon",transform:this.getInstanceIconFrame},instanceColorModes:{size:1,type:"uint8",accessor:"getIcon",transform:this.getInstanceColorMode},instanceColors:{size:this.props.colorFormat.length,type:"unorm8",transition:!0,accessor:"getColor",defaultValue:ge},instanceAngles:{size:1,transition:!0,accessor:"getAngle"},instancePixelOffset:{size:2,transition:!0,accessor:"getPixelOffset"}})}updateState(e){super.updateState(e);const{props:t,oldProps:i,changeFlags:s}=e,o=this.getAttributeManager(),{iconAtlas:a,iconMapping:n,data:r,getIcon:l,textureParameters:d}=t,{iconManager:u}=this.state;if(typeof a=="string")return;const g=a||this.internalState.isAsyncPropLoading("iconAtlas");u.setProps({loadOptions:t.loadOptions,autoPacking:!g,iconAtlas:a,iconMapping:g?n:null,textureParameters:d}),g?i.iconMapping!==t.iconMapping&&o.invalidate("getIcon"):(s.dataChanged||s.updateTriggersChanged&&(s.updateTriggersChanged.all||s.updateTriggersChanged.getIcon))&&u.packIcons(r,l),s.extensionsChanged&&(this.state.model?.destroy(),this.state.model=this._getModel(),o.invalidateAll())}get isLoaded(){return super.isLoaded&&this.state.iconManager.isLoaded}finalizeState(e){super.finalizeState(e),this.state.iconManager.finalize()}draw({uniforms:e}){const{sizeScale:t,sizeMinPixels:i,sizeMaxPixels:s,sizeUnits:o,billboard:a,alphaCutoff:n}=this.props,{iconManager:r}=this.state,l=r.getTexture();if(l){const d=this.state.model,u={iconsTexture:l,iconsTextureDim:[l.width,l.height],sizeUnits:w[o],sizeScale:t,sizeMinPixels:i,sizeMaxPixels:s,billboard:a,alphaCutoff:n};d.shaderInputs.setProps({icon:u}),d.draw(this.context.renderPass)}}_getModel(){const e=[-1,-1,1,-1,-1,1,1,1];return new D(this.context.device,{...this.getShaders(),id:this.props.id,bufferLayout:this.getAttributeManager().getBufferLayouts(),geometry:new N({topology:"triangle-strip",attributes:{positions:{size:2,value:new Float32Array(e)}}}),isInstanced:!0})}_onUpdate(){this.setNeedsRedraw()}_onError(e){const t=this.getCurrentLayer()?.props.onIconError;t?t(e):A.error(e.error.message)()}getInstanceOffset(e){const{width:t,height:i,anchorX:s=t/2,anchorY:o=i/2}=this.state.iconManager.getIconMapping(e);return[t/2-s,i/2-o]}getInstanceColorMode(e){return this.state.iconManager.getIconMapping(e).mask?1:0}getInstanceIconFrame(e){const{x:t,y:i,width:s,height:o}=this.state.iconManager.getIconMapping(e);return[t,i,s,o]}}G.defaultProps=Be;G.layerName="IconLayer";const Z=`uniform scatterplotUniforms {
  float radiusScale;
  float radiusMinPixels;
  float radiusMaxPixels;
  float lineWidthScale;
  float lineWidthMinPixels;
  float lineWidthMaxPixels;
  float stroked;
  float filled;
  bool antialiasing;
  bool billboard;
  highp int radiusUnits;
  highp int lineWidthUnits;
} scatterplot;
`,Ue={name:"scatterplot",vs:Z,fs:Z,source:"",uniformTypes:{radiusScale:"f32",radiusMinPixels:"f32",radiusMaxPixels:"f32",lineWidthScale:"f32",lineWidthMinPixels:"f32",lineWidthMaxPixels:"f32",stroked:"f32",filled:"f32",antialiasing:"f32",billboard:"f32",radiusUnits:"i32",lineWidthUnits:"i32"}},De=`#version 300 es
#define SHADER_NAME scatterplot-layer-vertex-shader
in vec3 positions;
in vec3 instancePositions;
in vec3 instancePositions64Low;
in float instanceRadius;
in float instanceLineWidths;
in vec4 instanceFillColors;
in vec4 instanceLineColors;
in vec3 instancePickingColors;
out vec4 vFillColor;
out vec4 vLineColor;
out vec2 unitPosition;
out float innerUnitRadius;
out float outerRadiusPixels;
void main(void) {
geometry.worldPosition = instancePositions;
outerRadiusPixels = clamp(
project_size_to_pixel(scatterplot.radiusScale * instanceRadius, scatterplot.radiusUnits),
scatterplot.radiusMinPixels, scatterplot.radiusMaxPixels
);
float lineWidthPixels = clamp(
project_size_to_pixel(scatterplot.lineWidthScale * instanceLineWidths, scatterplot.lineWidthUnits),
scatterplot.lineWidthMinPixels, scatterplot.lineWidthMaxPixels
);
outerRadiusPixels += scatterplot.stroked * lineWidthPixels / 2.0;
float edgePadding = scatterplot.antialiasing ? (outerRadiusPixels + SMOOTH_EDGE_RADIUS) / outerRadiusPixels : 1.0;
unitPosition = edgePadding * positions.xy;
geometry.uv = unitPosition;
geometry.pickingColor = instancePickingColors;
innerUnitRadius = 1.0 - scatterplot.stroked * lineWidthPixels / outerRadiusPixels;
if (scatterplot.billboard) {
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, vec3(0.0), geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
vec3 offset = edgePadding * positions * outerRadiusPixels;
DECKGL_FILTER_SIZE(offset, geometry);
gl_Position.xy += project_pixel_size_to_clipspace(offset.xy);
} else {
vec3 offset = edgePadding * positions * project_pixel_size(outerRadiusPixels);
DECKGL_FILTER_SIZE(offset, geometry);
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, offset, geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
}
vFillColor = vec4(instanceFillColors.rgb, instanceFillColors.a * layer.opacity);
DECKGL_FILTER_COLOR(vFillColor, geometry);
vLineColor = vec4(instanceLineColors.rgb, instanceLineColors.a * layer.opacity);
DECKGL_FILTER_COLOR(vLineColor, geometry);
}
`,Ne=`#version 300 es
#define SHADER_NAME scatterplot-layer-fragment-shader
precision highp float;
in vec4 vFillColor;
in vec4 vLineColor;
in vec2 unitPosition;
in float innerUnitRadius;
in float outerRadiusPixels;
out vec4 fragColor;
void main(void) {
geometry.uv = unitPosition;
float distToCenter = length(unitPosition) * outerRadiusPixels;
float inCircle = scatterplot.antialiasing ?
smoothedge(distToCenter, outerRadiusPixels) :
step(distToCenter, outerRadiusPixels);
if (inCircle == 0.0) {
discard;
}
if (scatterplot.stroked > 0.5) {
float isLine = scatterplot.antialiasing ?
smoothedge(innerUnitRadius * outerRadiusPixels, distToCenter) :
step(innerUnitRadius * outerRadiusPixels, distToCenter);
if (scatterplot.filled > 0.5) {
fragColor = mix(vFillColor, vLineColor, isLine);
} else {
if (isLine == 0.0) {
discard;
}
fragColor = vec4(vLineColor.rgb, vLineColor.a * isLine);
}
} else if (scatterplot.filled < 0.5) {
discard;
} else {
fragColor = vFillColor;
}
fragColor.a *= inCircle;
DECKGL_FILTER_COLOR(fragColor, geometry);
}
`,Ge=`// TODO(ibgreen): Hack for Layer uniforms (move to new "color" module?)

struct LayerUniforms {
  opacity: f32,
};

var<private> layer: LayerUniforms = LayerUniforms(1.0);
// @group(0) @binding(1) var<uniform> layer: LayerUniforms;

// Main shaders

struct ScatterplotUniforms {
  radiusScale: f32,
  radiusMinPixels: f32,
  radiusMaxPixels: f32,
  lineWidthScale: f32,
  lineWidthMinPixels: f32,
  lineWidthMaxPixels: f32,
  stroked: f32,
  filled: i32,
  antialiasing: i32,
  billboard: i32,
  radiusUnits: i32,
  lineWidthUnits: i32,
};

struct ConstantAttributeUniforms {
 instancePositions: vec3<f32>,
 instancePositions64Low: vec3<f32>,
 instanceRadius: f32,
 instanceLineWidths: f32,
 instanceFillColors: vec4<f32>,
 instanceLineColors: vec4<f32>,
 instancePickingColors: vec3<f32>,

 instancePositionsConstant: i32,
 instancePositions64LowConstant: i32,
 instanceRadiusConstant: i32,
 instanceLineWidthsConstant: i32,
 instanceFillColorsConstant: i32,
 instanceLineColorsConstant: i32,
 instancePickingColorsConstant: i32
};

@group(0) @binding(2) var<uniform> scatterplot: ScatterplotUniforms;

struct ConstantAttributes {
  instancePositions: vec3<f32>,
  instancePositions64Low: vec3<f32>,
  instanceRadius: f32,
  instanceLineWidths: f32,
  instanceFillColors: vec4<f32>,
  instanceLineColors: vec4<f32>,
  instancePickingColors: vec3<f32>
};

const constants = ConstantAttributes(
  vec3<f32>(0.0),
  vec3<f32>(0.0),
  0.0,
  0.0,
  vec4<f32>(0.0, 0.0, 0.0, 1.0),
  vec4<f32>(0.0, 0.0, 0.0, 1.0),
  vec3<f32>(0.0)
);

struct Attributes {
  @builtin(instance_index) instanceIndex : u32,
  @builtin(vertex_index) vertexIndex : u32,
  @location(0) positions: vec3<f32>,
  @location(1) instancePositions: vec3<f32>,
  @location(2) instancePositions64Low: vec3<f32>,
  @location(3) instanceRadius: f32,
  @location(4) instanceLineWidths: f32,
  @location(5) instanceFillColors: vec4<f32>,
  @location(6) instanceLineColors: vec4<f32>,
  @location(7) instancePickingColors: vec3<f32>
};

struct Varyings {
  @builtin(position) position: vec4<f32>,
  @location(0) vFillColor: vec4<f32>,
  @location(1) vLineColor: vec4<f32>,
  @location(2) unitPosition: vec2<f32>,
  @location(3) innerUnitRadius: f32,
  @location(4) outerRadiusPixels: f32,
};

@vertex
fn vertexMain(attributes: Attributes) -> Varyings {
  var varyings: Varyings;

  // Draw an inline geometry constant array clip space triangle to verify that rendering works.
  // var positions = array<vec2<f32>, 3>(vec2(0.0, 0.5), vec2(-0.5, -0.5), vec2(0.5, -0.5));
  // if (attributes.instanceIndex == 0) {
  //   varyings.position = vec4<f32>(positions[attributes.vertexIndex], 0.0, 1.0);
  //   return varyings;
  // }

  // var geometry: Geometry;
  // geometry.worldPosition = instancePositions;

  // Multiply out radius and clamp to limits
  varyings.outerRadiusPixels = clamp(
    project_unit_size_to_pixel(scatterplot.radiusScale * attributes.instanceRadius, scatterplot.radiusUnits),
    scatterplot.radiusMinPixels, scatterplot.radiusMaxPixels
  );

  // Multiply out line width and clamp to limits
  let lineWidthPixels = clamp(
    project_unit_size_to_pixel(scatterplot.lineWidthScale * attributes.instanceLineWidths, scatterplot.lineWidthUnits),
    scatterplot.lineWidthMinPixels, scatterplot.lineWidthMaxPixels
  );

  // outer radius needs to offset by half stroke width
  varyings.outerRadiusPixels += scatterplot.stroked * lineWidthPixels / 2.0;
  // Expand geometry to accommodate edge smoothing
  let edgePadding = select(
    (varyings.outerRadiusPixels + SMOOTH_EDGE_RADIUS) / varyings.outerRadiusPixels,
    1.0,
    scatterplot.antialiasing != 0
  );

  // position on the containing square in [-1, 1] space
  varyings.unitPosition = edgePadding * attributes.positions.xy;
  geometry.uv = varyings.unitPosition;
  geometry.pickingColor = attributes.instancePickingColors;

  varyings.innerUnitRadius = 1.0 - scatterplot.stroked * lineWidthPixels / varyings.outerRadiusPixels;

  if (scatterplot.billboard != 0) {
    varyings.position = project_position_to_clipspace(attributes.instancePositions, attributes.instancePositions64Low, vec3<f32>(0.0)); // TODO , geometry.position);
    // DECKGL_FILTER_GL_POSITION(varyings.position, geometry);
    let offset = attributes.positions; // * edgePadding * varyings.outerRadiusPixels;
    // DECKGL_FILTER_SIZE(offset, geometry);
    let clipPixels = project_pixel_size_to_clipspace(offset.xy);
    varyings.position.x = clipPixels.x;
    varyings.position.y = clipPixels.y;
  } else {
    let offset = edgePadding * attributes.positions * project_pixel_size_float(varyings.outerRadiusPixels);
    // DECKGL_FILTER_SIZE(offset, geometry);
    varyings.position = project_position_to_clipspace(attributes.instancePositions, attributes.instancePositions64Low, offset); // TODO , geometry.position);
    // DECKGL_FILTER_GL_POSITION(varyings.position, geometry);
  }

  // Apply opacity to instance color, or return instance picking color
  varyings.vFillColor = vec4<f32>(attributes.instanceFillColors.rgb, attributes.instanceFillColors.a * layer.opacity);
  // DECKGL_FILTER_COLOR(varyings.vFillColor, geometry);
  varyings.vLineColor = vec4<f32>(attributes.instanceLineColors.rgb, attributes.instanceLineColors.a * layer.opacity);
  // DECKGL_FILTER_COLOR(varyings.vLineColor, geometry);

  return varyings;
}

@fragment
fn fragmentMain(varyings: Varyings) -> @location(0) vec4<f32> {
  // var geometry: Geometry;
  // geometry.uv = unitPosition;

  let distToCenter = length(varyings.unitPosition) * varyings.outerRadiusPixels;
  let inCircle = select(
    smoothedge(distToCenter, varyings.outerRadiusPixels),
    step(distToCenter, varyings.outerRadiusPixels),
    scatterplot.antialiasing != 0
  );

  if (inCircle == 0.0) {
    // discard;
  }

  var fragColor: vec4<f32>;

  if (scatterplot.stroked != 0) {
    let isLine = select(
      smoothedge(varyings.innerUnitRadius * varyings.outerRadiusPixels, distToCenter),
      step(varyings.innerUnitRadius * varyings.outerRadiusPixels, distToCenter),
      scatterplot.antialiasing != 0
    );

    if (scatterplot.filled != 0) {
      fragColor = mix(varyings.vFillColor, varyings.vLineColor, isLine);
    } else {
      if (isLine == 0.0) {
        // discard;
      }
      fragColor = vec4<f32>(varyings.vLineColor.rgb, varyings.vLineColor.a * isLine);
    }
  } else if (scatterplot.filled == 0) {
    // discard;
  } else {
    fragColor = varyings.vFillColor;
  }

  fragColor.a *= inCircle;
  // DECKGL_FILTER_COLOR(fragColor, geometry);

  return fragColor;
  // return vec4<f32>(0, 0, 1, 1);
}
`,J=[0,0,0,255],He={radiusUnits:"meters",radiusScale:{type:"number",min:0,value:1},radiusMinPixels:{type:"number",min:0,value:0},radiusMaxPixels:{type:"number",min:0,value:Number.MAX_SAFE_INTEGER},lineWidthUnits:"meters",lineWidthScale:{type:"number",min:0,value:1},lineWidthMinPixels:{type:"number",min:0,value:0},lineWidthMaxPixels:{type:"number",min:0,value:Number.MAX_SAFE_INTEGER},stroked:!1,filled:!0,billboard:!1,antialiasing:!0,getPosition:{type:"accessor",value:c=>c.position},getRadius:{type:"accessor",value:1},getFillColor:{type:"accessor",value:J},getLineColor:{type:"accessor",value:J},getLineWidth:{type:"accessor",value:1},strokeWidth:{deprecatedFor:"getLineWidth"},outline:{deprecatedFor:"stroked"},getColor:{deprecatedFor:["getFillColor","getLineColor"]}};class fe extends F{getShaders(){return super.getShaders({vs:De,fs:Ne,source:Ge,modules:[B,U,Ue]})}initializeState(){this.getAttributeManager().addInstanced({instancePositions:{size:3,type:"float64",fp64:this.use64bitPositions(),transition:!0,accessor:"getPosition"},instanceRadius:{size:1,transition:!0,accessor:"getRadius",defaultValue:1},instanceFillColors:{size:this.props.colorFormat.length,transition:!0,type:"unorm8",accessor:"getFillColor",defaultValue:[0,0,0,255]},instanceLineColors:{size:this.props.colorFormat.length,transition:!0,type:"unorm8",accessor:"getLineColor",defaultValue:[0,0,0,255]},instanceLineWidths:{size:1,transition:!0,accessor:"getLineWidth",defaultValue:1}})}updateState(e){super.updateState(e),e.changeFlags.extensionsChanged&&(this.state.model?.destroy(),this.state.model=this._getModel(),this.getAttributeManager().invalidateAll())}draw({uniforms:e}){const{radiusUnits:t,radiusScale:i,radiusMinPixels:s,radiusMaxPixels:o,stroked:a,filled:n,billboard:r,antialiasing:l,lineWidthUnits:d,lineWidthScale:u,lineWidthMinPixels:g,lineWidthMaxPixels:f}=this.props,p={stroked:a,filled:n,billboard:r,antialiasing:l,radiusUnits:w[t],radiusScale:i,radiusMinPixels:s,radiusMaxPixels:o,lineWidthUnits:w[d],lineWidthScale:u,lineWidthMinPixels:g,lineWidthMaxPixels:f},x=this.state.model;x.shaderInputs.setProps({scatterplot:p}),x.draw(this.context.renderPass)}_getModel(){const e=[-1,-1,0,1,-1,0,-1,1,0,1,1,0];return new D(this.context.device,{...this.getShaders(),id:this.props.id,bufferLayout:this.getAttributeManager().getBufferLayouts(),geometry:new N({topology:"triangle-strip",attributes:{positions:{size:3,value:new Float32Array(e)}}}),isInstanced:!0})}}fe.defaultProps=He;fe.layerName="ScatterplotLayer";const Q=`uniform sdfUniforms {
  float gamma;
  bool enabled;
  float buffer;
  float outlineBuffer;
  vec4 outlineColor;
} sdf;
`,je={name:"sdf",vs:Q,fs:Q,uniformTypes:{gamma:"f32",enabled:"f32",buffer:"f32",outlineBuffer:"f32",outlineColor:"vec4<f32>"}},$e=`#version 300 es
#define SHADER_NAME multi-icon-layer-fragment-shader
precision highp float;
uniform sampler2D iconsTexture;
in vec4 vColor;
in vec2 vTextureCoords;
in vec2 uv;
out vec4 fragColor;
void main(void) {
geometry.uv = uv;
if (!bool(picking.isActive)) {
float alpha = texture(iconsTexture, vTextureCoords).a;
vec4 color = vColor;
if (sdf.enabled) {
float distance = alpha;
alpha = smoothstep(sdf.buffer - sdf.gamma, sdf.buffer + sdf.gamma, distance);
if (sdf.outlineBuffer > 0.0) {
float inFill = alpha;
float inBorder = smoothstep(sdf.outlineBuffer - sdf.gamma, sdf.outlineBuffer + sdf.gamma, distance);
color = mix(sdf.outlineColor, vColor, inFill);
alpha = inBorder;
}
}
float a = alpha * color.a;
if (a < icon.alphaCutoff) {
discard;
}
fragColor = vec4(color.rgb, a * layer.opacity);
}
DECKGL_FILTER_COLOR(fragColor, geometry);
}
`,k=192/256,ee=[],Ke={getIconOffsets:{type:"accessor",value:c=>c.offsets},alphaCutoff:.001,smoothing:.1,outlineWidth:0,outlineColor:{type:"color",value:[0,0,0,255]}};class H extends G{getShaders(){const e=super.getShaders();return{...e,modules:[...e.modules,je],fs:$e}}initializeState(){super.initializeState(),this.getAttributeManager().addInstanced({instanceOffsets:{size:2,accessor:"getIconOffsets"},instancePickingColors:{type:"uint8",size:3,accessor:(t,{index:i,target:s})=>this.encodePickingColor(i,s)}})}updateState(e){super.updateState(e);const{props:t,oldProps:i}=e;let{outlineColor:s}=t;s!==i.outlineColor&&(s=s.map(o=>o/255),s[3]=Number.isFinite(s[3])?s[3]:1,this.setState({outlineColor:s})),!t.sdf&&t.outlineWidth&&A.warn(`${this.id}: fontSettings.sdf is required to render outline`)()}draw(e){const{sdf:t,smoothing:i,outlineWidth:s}=this.props,{outlineColor:o}=this.state,a=s?Math.max(i,k*(1-s)):-1,n=this.state.model,r={buffer:k,outlineBuffer:a,gamma:i,enabled:!!t,outlineColor:o};if(n.shaderInputs.setProps({sdf:r}),super.draw(e),t&&s){const{iconManager:l}=this.state;l.getTexture()&&(n.shaderInputs.setProps({sdf:{...r,outlineBuffer:k}}),n.draw(this.context.renderPass))}}getInstanceOffset(e){return e?Array.from(e).flatMap(t=>super.getInstanceOffset(t)):ee}getInstanceColorMode(e){return 1}getInstanceIconFrame(e){return e?Array.from(e).flatMap(t=>super.getInstanceIconFrame(t)):ee}}H.defaultProps=Ke;H.layerName="MultiIconLayer";const z=1e20;class Ve{constructor({fontSize:e=24,buffer:t=3,radius:i=8,cutoff:s=.25,fontFamily:o="sans-serif",fontWeight:a="normal",fontStyle:n="normal",lang:r=null}={}){this.buffer=t,this.cutoff=s,this.radius=i,this.lang=r;const l=this.size=e+t*4,d=this._createCanvas(l),u=this.ctx=d.getContext("2d",{willReadFrequently:!0});u.font=`${n} ${a} ${e}px ${o}`,u.textBaseline="alphabetic",u.textAlign="left",u.fillStyle="black",this.gridOuter=new Float64Array(l*l),this.gridInner=new Float64Array(l*l),this.f=new Float64Array(l),this.z=new Float64Array(l+1),this.v=new Uint16Array(l)}_createCanvas(e){const t=document.createElement("canvas");return t.width=t.height=e,t}draw(e){const{width:t,actualBoundingBoxAscent:i,actualBoundingBoxDescent:s,actualBoundingBoxLeft:o,actualBoundingBoxRight:a}=this.ctx.measureText(e),n=Math.ceil(i),r=0,l=Math.max(0,Math.min(this.size-this.buffer,Math.ceil(a-o))),d=Math.min(this.size-this.buffer,n+Math.ceil(s)),u=l+2*this.buffer,g=d+2*this.buffer,f=Math.max(u*g,0),p=new Uint8ClampedArray(f),x={data:p,width:u,height:g,glyphWidth:l,glyphHeight:d,glyphTop:n,glyphLeft:r,glyphAdvance:t};if(l===0||d===0)return x;const{ctx:h,buffer:v,gridInner:P,gridOuter:m}=this;this.lang&&(h.lang=this.lang),h.clearRect(v,v,l,d),h.fillText(e,v,v+n);const L=h.getImageData(v,v,l,d);m.fill(z,0,f),P.fill(0,0,f);for(let _=0;_<d;_++)for(let y=0;y<l;y++){const M=L.data[4*(_*l+y)+3]/255;if(M===0)continue;const b=(_+v)*u+y+v;if(M===1)m[b]=0,P[b]=z;else{const S=.5-M;m[b]=S>0?S*S:0,P[b]=S<0?S*S:0}}te(m,0,0,u,g,u,this.f,this.v,this.z),te(P,v,v,l,d,u,this.f,this.v,this.z);for(let _=0;_<f;_++){const y=Math.sqrt(m[_])-Math.sqrt(P[_]);p[_]=Math.round(255-255*(y/this.radius+this.cutoff))}return x}}function te(c,e,t,i,s,o,a,n,r){for(let l=e;l<e+i;l++)ie(c,t*o+l,o,s,a,n,r);for(let l=t;l<t+s;l++)ie(c,l*o+e,1,i,a,n,r)}function ie(c,e,t,i,s,o,a){o[0]=0,a[0]=-z,a[1]=z,s[0]=c[e];for(let n=1,r=0,l=0;n<i;n++){s[n]=c[e+n*t];const d=n*n;do{const u=o[r];l=(s[n]-s[u]+d-u*u)/(n-u)/2}while(l<=a[r]&&--r>-1);r++,o[r]=n,a[r]=l,a[r+1]=z}for(let n=0,r=0;n<i;n++){for(;a[r+1]<n;)r++;const l=o[r],d=n-l;c[e+n*t]=s[l]+d*d}}const qe=32,Ye=[];function Xe(c){return Math.pow(2,Math.ceil(Math.log2(c)))}function Ze({characterSet:c,getFontWidth:e,fontHeight:t,buffer:i,maxCanvasWidth:s,mapping:o={},xOffset:a=0,yOffset:n=0}){let r=0,l=a;const d=t+i*2;for(const u of c)if(!o[u]){const g=e(u);l+g+i*2>s&&(l=0,r++),o[u]={x:l+i,y:n+r*d+i,width:g,height:d,layoutWidth:g,layoutHeight:t},l+=g+i*2}return{mapping:o,xOffset:l,yOffset:n+r*d,canvasHeight:Xe(n+(r+1)*d)}}function pe(c,e,t,i){let s=0;for(let o=e;o<t;o++){const a=c[o];s+=i[a]?.layoutWidth||0}return s}function he(c,e,t,i,s,o){let a=e,n=0;for(let r=e;r<t;r++){const l=pe(c,r,r+1,s);n+l>i&&(a<r&&o.push(r),a=r,n=0),n+=l}return n}function Je(c,e,t,i,s,o){let a=e,n=e,r=e,l=0;for(let d=e;d<t;d++)if((c[d]===" "||c[d+1]===" "||d+1===t)&&(r=d+1),r>n){let u=pe(c,n,r,s);l+u>i&&(a<n&&(o.push(n),a=n,l=0),u>i&&(u=he(c,n,r,i,s,o),a=o[o.length-1])),n=r,l+=u}return l}function Qe(c,e,t,i,s=0,o){o===void 0&&(o=c.length);const a=[];return e==="break-all"?he(c,s,o,t,i,a):Je(c,s,o,t,i,a),a}function et(c,e,t,i,s,o){let a=0,n=0;for(let r=e;r<t;r++){const l=c[r],d=i[l];d?(n||(n=d.layoutHeight),s[r]=a+d.layoutWidth/2,a+=d.layoutWidth):(A.warn(`Missing character: ${l} (${l.codePointAt(0)})`)(),s[r]=a,a+=qe)}o[0]=a,o[1]=n}function tt(c,e,t,i,s){const o=Array.from(c),a=o.length,n=new Array(a),r=new Array(a),l=new Array(a),d=(t==="break-word"||t==="break-all")&&isFinite(i)&&i>0,u=[0,0],g=[0,0];let f=0,p=0,x=0;for(let h=0;h<=a;h++){const v=o[h];if((v===`
`||h===a)&&(x=h),x>p){const P=d?Qe(o,t,i,s,p,x):Ye;for(let m=0;m<=P.length;m++){const L=m===0?p:P[m-1],_=m<P.length?P[m]:x;et(o,L,_,s,n,g);for(let y=L;y<_;y++){n[y]-g[0]/2;const M=o[y],b=s[M]?.layoutOffsetY||0;r[y]=f+g[1]/2+b,l[y]=g[0]}f=f+g[1]*e,u[0]=Math.max(u[0],g[0])}p=x}v===`
`&&(n[p]=0,r[p]=0,l[p]=0,p++)}return u[1]=f,{x:n,y:r,rowWidth:l,size:u}}function it({value:c,length:e,stride:t,offset:i,startIndices:s,characterSet:o}){const a=c.BYTES_PER_ELEMENT,n=t?t/a:1,r=i?i/a:0,l=s[e]||Math.ceil((c.length-r)/n),d=o&&new Set,u=new Array(e);let g=c;if(n>1||r>0){const f=c.constructor;g=new f(l);for(let p=0;p<l;p++)g[p]=c[p*n+r]}for(let f=0;f<e;f++){const p=s[f],x=s[f+1]||l,h=g.subarray(p,x);u[f]=String.fromCodePoint.apply(null,h),d&&h.forEach(d.add,d)}if(d)for(const f of d)o.add(String.fromCodePoint(f));return{texts:u,characterCount:l}}class xe{constructor(e=5){this._cache={},this._order=[],this.limit=e}get(e){const t=this._cache[e];return t&&(this._deleteOrder(e),this._appendOrder(e)),t}set(e,t){this._cache[e]?(this.delete(e),this._cache[e]=t,this._appendOrder(e)):(Object.keys(this._cache).length===this.limit&&this.delete(this._order[0]),this._cache[e]=t,this._appendOrder(e))}delete(e){this._cache[e]&&(delete this._cache[e],this._deleteOrder(e))}_deleteOrder(e){const t=this._order.indexOf(e);t>=0&&this._order.splice(t,1)}_appendOrder(e){this._order.push(e)}}function st(){const c=[];for(let e=32;e<128;e++)c.push(String.fromCharCode(e));return c}const I={fontFamily:"Monaco, monospace",fontWeight:"normal",characterSet:st(),fontSize:64,buffer:4,sdf:!1,cutoff:.25,radius:12,smoothing:.1},se=1024,oe=.9,ne=1.2,me=3;let O=new xe(me);function ot(c,e){let t;typeof e=="string"?t=new Set(Array.from(e)):t=new Set(e);const i=O.get(c);if(!i)return t;for(const s in i.mapping)t.has(s)&&t.delete(s);return t}function nt(c,e){for(let t=0;t<c.length;t++)e.data[4*t+3]=c[t]}function ae(c,e,t,i){c.font=`${i} ${t}px ${e}`,c.fillStyle="#000",c.textBaseline="alphabetic",c.textAlign="left"}function at(c){A.assert(Number.isFinite(c)&&c>=me,"Invalid cache limit"),O=new xe(c)}class rt{constructor(){this.props={...I}}get atlas(){return this._atlas}get mapping(){return this._atlas&&this._atlas.mapping}get scale(){const{fontSize:e,buffer:t}=this.props;return(e*ne+t*2)/e}setProps(e={}){Object.assign(this.props,e),this._key=this._getKey();const t=ot(this._key,this.props.characterSet),i=O.get(this._key);if(i&&t.size===0){this._atlas!==i&&(this._atlas=i);return}const s=this._generateFontAtlas(t,i);this._atlas=s,O.set(this._key,s)}_generateFontAtlas(e,t){const{fontFamily:i,fontWeight:s,fontSize:o,buffer:a,sdf:n,radius:r,cutoff:l}=this.props;let d=t&&t.data;d||(d=document.createElement("canvas"),d.width=se);const u=d.getContext("2d",{willReadFrequently:!0});ae(u,i,o,s);const{mapping:g,canvasHeight:f,xOffset:p,yOffset:x}=Ze({getFontWidth:h=>u.measureText(h).width,fontHeight:o*ne,buffer:a,characterSet:e,maxCanvasWidth:se,...t&&{mapping:t.mapping,xOffset:t.xOffset,yOffset:t.yOffset}});if(d.height!==f){const h=u.getImageData(0,0,d.width,d.height);d.height=f,u.putImageData(h,0,0)}if(ae(u,i,o,s),n){const h=new Ve({fontSize:o,buffer:a,radius:r,cutoff:l,fontFamily:i,fontWeight:`${s}`});for(const v of e){const{data:P,width:m,height:L,glyphTop:_}=h.draw(v);g[v].width=m,g[v].layoutOffsetY=o*oe-_;const y=u.createImageData(m,L);nt(P,y),u.putImageData(y,g[v].x,g[v].y)}}else for(const h of e)u.fillText(h,g[h].x,g[h].y+a+o*oe);return{xOffset:p,yOffset:x,mapping:g,data:d,width:d.width,height:d.height}}_getKey(){const{fontFamily:e,fontWeight:t,fontSize:i,buffer:s,sdf:o,radius:a,cutoff:n}=this.props;return o?`${e} ${t} ${i} ${s} ${a} ${n}`:`${e} ${t} ${i} ${s}`}}const re=`uniform textBackgroundUniforms {
  bool billboard;
  float sizeScale;
  float sizeMinPixels;
  float sizeMaxPixels;
  vec4 borderRadius;
  vec4 padding;
  highp int sizeUnits;
  bool stroked;
} textBackground;
`,lt={name:"textBackground",vs:re,fs:re,uniformTypes:{billboard:"f32",sizeScale:"f32",sizeMinPixels:"f32",sizeMaxPixels:"f32",borderRadius:"vec4<f32>",padding:"vec4<f32>",sizeUnits:"i32",stroked:"f32"}},ct=`#version 300 es
#define SHADER_NAME text-background-layer-vertex-shader
in vec2 positions;
in vec3 instancePositions;
in vec3 instancePositions64Low;
in vec4 instanceRects;
in float instanceSizes;
in float instanceAngles;
in vec2 instancePixelOffsets;
in float instanceLineWidths;
in vec4 instanceFillColors;
in vec4 instanceLineColors;
in vec3 instancePickingColors;
out vec4 vFillColor;
out vec4 vLineColor;
out float vLineWidth;
out vec2 uv;
out vec2 dimensions;
vec2 rotate_by_angle(vec2 vertex, float angle) {
float angle_radian = radians(angle);
float cos_angle = cos(angle_radian);
float sin_angle = sin(angle_radian);
mat2 rotationMatrix = mat2(cos_angle, -sin_angle, sin_angle, cos_angle);
return rotationMatrix * vertex;
}
void main(void) {
geometry.worldPosition = instancePositions;
geometry.uv = positions;
geometry.pickingColor = instancePickingColors;
uv = positions;
vLineWidth = instanceLineWidths;
float sizePixels = clamp(
project_size_to_pixel(instanceSizes * textBackground.sizeScale, textBackground.sizeUnits),
textBackground.sizeMinPixels, textBackground.sizeMaxPixels
);
dimensions = instanceRects.zw * sizePixels + textBackground.padding.xy + textBackground.padding.zw;
vec2 pixelOffset = (positions * instanceRects.zw + instanceRects.xy) * sizePixels + mix(-textBackground.padding.xy, textBackground.padding.zw, positions);
pixelOffset = rotate_by_angle(pixelOffset, instanceAngles);
pixelOffset += instancePixelOffsets;
pixelOffset.y *= -1.0;
if (textBackground.billboard)  {
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, vec3(0.0), geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
vec3 offset = vec3(pixelOffset, 0.0);
DECKGL_FILTER_SIZE(offset, geometry);
gl_Position.xy += project_pixel_size_to_clipspace(offset.xy);
} else {
vec3 offset_common = vec3(project_pixel_size(pixelOffset), 0.0);
DECKGL_FILTER_SIZE(offset_common, geometry);
gl_Position = project_position_to_clipspace(instancePositions, instancePositions64Low, offset_common, geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
}
vFillColor = vec4(instanceFillColors.rgb, instanceFillColors.a * layer.opacity);
DECKGL_FILTER_COLOR(vFillColor, geometry);
vLineColor = vec4(instanceLineColors.rgb, instanceLineColors.a * layer.opacity);
DECKGL_FILTER_COLOR(vLineColor, geometry);
}
`,dt=`#version 300 es
#define SHADER_NAME text-background-layer-fragment-shader
precision highp float;
in vec4 vFillColor;
in vec4 vLineColor;
in float vLineWidth;
in vec2 uv;
in vec2 dimensions;
out vec4 fragColor;
float round_rect(vec2 p, vec2 size, vec4 radii) {
vec2 pixelPositionCB = (p - 0.5) * size;
vec2 sizeCB = size * 0.5;
float maxBorderRadius = min(size.x, size.y) * 0.5;
vec4 borderRadius = vec4(min(radii, maxBorderRadius));
borderRadius.xy =
(pixelPositionCB.x > 0.0) ? borderRadius.xy : borderRadius.zw;
borderRadius.x = (pixelPositionCB.y > 0.0) ? borderRadius.x : borderRadius.y;
vec2 q = abs(pixelPositionCB) - sizeCB + borderRadius.x;
return -(min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - borderRadius.x);
}
float rect(vec2 p, vec2 size) {
vec2 pixelPosition = p * size;
return min(min(pixelPosition.x, size.x - pixelPosition.x),
min(pixelPosition.y, size.y - pixelPosition.y));
}
vec4 get_stroked_fragColor(float dist) {
float isBorder = smoothedge(dist, vLineWidth);
return mix(vFillColor, vLineColor, isBorder);
}
void main(void) {
geometry.uv = uv;
if (textBackground.borderRadius != vec4(0.0)) {
float distToEdge = round_rect(uv, dimensions, textBackground.borderRadius);
if (textBackground.stroked) {
fragColor = get_stroked_fragColor(distToEdge);
} else {
fragColor = vFillColor;
}
float shapeAlpha = smoothedge(-distToEdge, 0.0);
fragColor.a *= shapeAlpha;
} else {
if (textBackground.stroked) {
float distToEdge = rect(uv, dimensions);
fragColor = get_stroked_fragColor(distToEdge);
} else {
fragColor = vFillColor;
}
}
DECKGL_FILTER_COLOR(fragColor, geometry);
}
`,ut={billboard:!0,sizeScale:1,sizeUnits:"pixels",sizeMinPixels:0,sizeMaxPixels:Number.MAX_SAFE_INTEGER,borderRadius:{type:"object",value:0},padding:{type:"array",value:[0,0,0,0]},getPosition:{type:"accessor",value:c=>c.position},getSize:{type:"accessor",value:1},getAngle:{type:"accessor",value:0},getPixelOffset:{type:"accessor",value:[0,0]},getBoundingRect:{type:"accessor",value:[0,0,0,0]},getFillColor:{type:"accessor",value:[0,0,0,255]},getLineColor:{type:"accessor",value:[0,0,0,255]},getLineWidth:{type:"accessor",value:1}};class j extends F{getShaders(){return super.getShaders({vs:ct,fs:dt,modules:[B,U,lt]})}initializeState(){this.getAttributeManager().addInstanced({instancePositions:{size:3,type:"float64",fp64:this.use64bitPositions(),transition:!0,accessor:"getPosition"},instanceSizes:{size:1,transition:!0,accessor:"getSize",defaultValue:1},instanceAngles:{size:1,transition:!0,accessor:"getAngle"},instanceRects:{size:4,accessor:"getBoundingRect"},instancePixelOffsets:{size:2,transition:!0,accessor:"getPixelOffset"},instanceFillColors:{size:4,transition:!0,type:"unorm8",accessor:"getFillColor",defaultValue:[0,0,0,255]},instanceLineColors:{size:4,transition:!0,type:"unorm8",accessor:"getLineColor",defaultValue:[0,0,0,255]},instanceLineWidths:{size:1,transition:!0,accessor:"getLineWidth",defaultValue:1}})}updateState(e){super.updateState(e);const{changeFlags:t}=e;t.extensionsChanged&&(this.state.model?.destroy(),this.state.model=this._getModel(),this.getAttributeManager().invalidateAll())}draw({uniforms:e}){const{billboard:t,sizeScale:i,sizeUnits:s,sizeMinPixels:o,sizeMaxPixels:a,getLineWidth:n}=this.props;let{padding:r,borderRadius:l}=this.props;r.length<4&&(r=[r[0],r[1],r[0],r[1]]),Array.isArray(l)||(l=[l,l,l,l]);const d=this.state.model,u={billboard:t,stroked:!!n,borderRadius:l,padding:r,sizeUnits:w[s],sizeScale:i,sizeMinPixels:o,sizeMaxPixels:a};d.shaderInputs.setProps({textBackground:u}),d.draw(this.context.renderPass)}_getModel(){const e=[0,0,1,0,0,1,1,1];return new D(this.context.device,{...this.getShaders(),id:this.props.id,bufferLayout:this.getAttributeManager().getBufferLayouts(),geometry:new N({topology:"triangle-strip",vertexCount:4,attributes:{positions:{size:2,value:new Float32Array(e)}}}),isInstanced:!0})}}j.defaultProps=ut;j.layerName="TextBackgroundLayer";const le={start:1,middle:0,end:-1},ce={top:1,center:0,bottom:-1},W=[0,0,0,255],gt=1,ft={billboard:!0,sizeScale:1,sizeUnits:"pixels",sizeMinPixels:0,sizeMaxPixels:Number.MAX_SAFE_INTEGER,background:!1,getBackgroundColor:{type:"accessor",value:[255,255,255,255]},getBorderColor:{type:"accessor",value:W},getBorderWidth:{type:"accessor",value:0},backgroundBorderRadius:{type:"object",value:0},backgroundPadding:{type:"array",value:[0,0,0,0]},characterSet:{type:"object",value:I.characterSet},fontFamily:I.fontFamily,fontWeight:I.fontWeight,lineHeight:gt,outlineWidth:{type:"number",value:0,min:0},outlineColor:{type:"color",value:W},fontSettings:{type:"object",value:{},compare:1},wordBreak:"break-word",maxWidth:{type:"number",value:-1},getText:{type:"accessor",value:c=>c.text},getPosition:{type:"accessor",value:c=>c.position},getColor:{type:"accessor",value:W},getSize:{type:"accessor",value:32},getAngle:{type:"accessor",value:0},getTextAnchor:{type:"accessor",value:"middle"},getAlignmentBaseline:{type:"accessor",value:"center"},getPixelOffset:{type:"accessor",value:[0,0]},backgroundColor:{deprecatedFor:["background","getBackgroundColor"]}};class ve extends ue{constructor(){super(...arguments),this.getBoundingRect=(e,t)=>{let{size:[i,s]}=this.transformParagraph(e,t);const{fontSize:o}=this.state.fontAtlasManager.props;i/=o,s/=o;const{getTextAnchor:a,getAlignmentBaseline:n}=this.props,r=le[typeof a=="function"?a(e,t):a],l=ce[typeof n=="function"?n(e,t):n];return[(r-1)*i/2,(l-1)*s/2,i,s]},this.getIconOffsets=(e,t)=>{const{getTextAnchor:i,getAlignmentBaseline:s}=this.props,{x:o,y:a,rowWidth:n,size:[r,l]}=this.transformParagraph(e,t),d=le[typeof i=="function"?i(e,t):i],u=ce[typeof s=="function"?s(e,t):s],g=o.length,f=new Array(g*2);let p=0;for(let x=0;x<g;x++){const h=(1-d)*(r-n[x])/2;f[p++]=(d-1)*r/2+h+o[x],f[p++]=(u-1)*l/2+a[x]}return f}}initializeState(){this.state={styleVersion:0,fontAtlasManager:new rt},this.props.maxWidth>0&&A.once(1,"v8.9 breaking change: TextLayer maxWidth is now relative to text size")()}updateState(e){const{props:t,oldProps:i,changeFlags:s}=e;(s.dataChanged||s.updateTriggersChanged&&(s.updateTriggersChanged.all||s.updateTriggersChanged.getText))&&this._updateText(),(this._updateFontAtlas()||t.lineHeight!==i.lineHeight||t.wordBreak!==i.wordBreak||t.maxWidth!==i.maxWidth)&&this.setState({styleVersion:this.state.styleVersion+1})}getPickingInfo({info:e}){return e.object=e.index>=0?this.props.data[e.index]:null,e}_updateFontAtlas(){const{fontSettings:e,fontFamily:t,fontWeight:i}=this.props,{fontAtlasManager:s,characterSet:o}=this.state,a={...e,characterSet:o,fontFamily:t,fontWeight:i};if(!s.mapping)return s.setProps(a),!0;for(const n in a)if(a[n]!==s.props[n])return s.setProps(a),!0;return!1}_updateText(){const{data:e,characterSet:t}=this.props,i=e.attributes?.getText;let{getText:s}=this.props,o=e.startIndices,a;const n=t==="auto"&&new Set;if(i&&o){const{texts:r,characterCount:l}=it({...ArrayBuffer.isView(i)?{value:i}:i,length:e.length,startIndices:o,characterSet:n});a=l,s=(d,{index:u})=>r[u]}else{const{iterable:r,objectInfo:l}=de(e);o=[0],a=0;for(const d of r){l.index++;const u=Array.from(s(d,l)||"");n&&u.forEach(n.add,n),a+=u.length,o.push(a)}}this.setState({getText:s,startIndices:o,numInstances:a,characterSet:n||t})}transformParagraph(e,t){const{fontAtlasManager:i}=this.state,s=i.mapping,o=this.state.getText,{wordBreak:a,lineHeight:n,maxWidth:r}=this.props,l=o(e,t)||"";return tt(l,n,a,r*i.props.fontSize,s)}renderLayers(){const{startIndices:e,numInstances:t,getText:i,fontAtlasManager:{scale:s,atlas:o,mapping:a},styleVersion:n}=this.state,{data:r,_dataDiff:l,getPosition:d,getColor:u,getSize:g,getAngle:f,getPixelOffset:p,getBackgroundColor:x,getBorderColor:h,getBorderWidth:v,backgroundBorderRadius:P,backgroundPadding:m,background:L,billboard:_,fontSettings:y,outlineWidth:M,outlineColor:b,sizeScale:S,sizeUnits:E,sizeMinPixels:$,sizeMaxPixels:K,transitions:T,updateTriggers:C}=this.props,ye=this.getSubLayerClass("characters",H),_e=this.getSubLayerClass("background",j);return[L&&new _e({getFillColor:x,getLineColor:h,getLineWidth:v,borderRadius:P,padding:m,getPosition:d,getSize:g,getAngle:f,getPixelOffset:p,billboard:_,sizeScale:S,sizeUnits:E,sizeMinPixels:$,sizeMaxPixels:K,transitions:T&&{getPosition:T.getPosition,getAngle:T.getAngle,getSize:T.getSize,getFillColor:T.getBackgroundColor,getLineColor:T.getBorderColor,getLineWidth:T.getBorderWidth,getPixelOffset:T.getPixelOffset}},this.getSubLayerProps({id:"background",updateTriggers:{getPosition:C.getPosition,getAngle:C.getAngle,getSize:C.getSize,getFillColor:C.getBackgroundColor,getLineColor:C.getBorderColor,getLineWidth:C.getBorderWidth,getPixelOffset:C.getPixelOffset,getBoundingRect:{getText:C.getText,getTextAnchor:C.getTextAnchor,getAlignmentBaseline:C.getAlignmentBaseline,styleVersion:n}}}),{data:r.attributes&&r.attributes.background?{length:r.length,attributes:r.attributes.background}:r,_dataDiff:l,autoHighlight:!1,getBoundingRect:this.getBoundingRect}),new ye({sdf:y.sdf,smoothing:Number.isFinite(y.smoothing)?y.smoothing:I.smoothing,outlineWidth:M/(y.radius||I.radius),outlineColor:b,iconAtlas:o,iconMapping:a,getPosition:d,getColor:u,getSize:g,getAngle:f,getPixelOffset:p,billboard:_,sizeScale:S*s,sizeUnits:E,sizeMinPixels:$*s,sizeMaxPixels:K*s,transitions:T&&{getPosition:T.getPosition,getAngle:T.getAngle,getColor:T.getColor,getSize:T.getSize,getPixelOffset:T.getPixelOffset}},this.getSubLayerProps({id:"characters",updateTriggers:{all:C.getText,getPosition:C.getPosition,getAngle:C.getAngle,getColor:C.getColor,getSize:C.getSize,getPixelOffset:C.getPixelOffset,getIconOffsets:{getTextAnchor:C.getTextAnchor,getAlignmentBaseline:C.getAlignmentBaseline,styleVersion:n}}}),{data:r,_dataDiff:l,startIndices:e,numInstances:t,getIconOffsets:this.getIconOffsets,getIcon:i})]}static set fontAtlasCacheLimit(e){at(e)}}ve.defaultProps=ft;ve.layerName="TextLayer";export{ue as C,G as I,fe as S,ve as T};
