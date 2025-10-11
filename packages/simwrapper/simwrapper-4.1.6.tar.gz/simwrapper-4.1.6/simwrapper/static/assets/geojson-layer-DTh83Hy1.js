import{T as kt,I as Wt,S as Ut,C as Vt}from"./text-layer-Cpq7KRgR.js";import{T as Bt,c as Ht,a as Zt,P as $t}from"./path-layer-BllYebBs.js";import{a as jt}from"./index-D3p5oi12.js";import{v as Xt,w as Jt,x as Kt,y as Yt,z as nt,B as rt,G as yt,q as W}from"./layer-GQvgsG1_.js";function We(o){throw new Error('Could not dynamically require "'+o+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.')}const xt=`precision highp int;

// #if (defined(SHADER_TYPE_FRAGMENT) && defined(LIGHTING_FRAGMENT)) || (defined(SHADER_TYPE_VERTEX) && defined(LIGHTING_VERTEX))
struct AmbientLight {
  vec3 color;
};

struct PointLight {
  vec3 color;
  vec3 position;
  vec3 attenuation; // 2nd order x:Constant-y:Linear-z:Exponential
};

struct DirectionalLight {
  vec3 color;
  vec3 direction;
};

uniform lightingUniforms {
  int enabled;
  int lightType;

  int directionalLightCount;
  int pointLightCount;

  vec3 ambientColor;

  vec3 lightColor0;
  vec3 lightPosition0;
  vec3 lightDirection0;
  vec3 lightAttenuation0;

  vec3 lightColor1;
  vec3 lightPosition1;
  vec3 lightDirection1;
  vec3 lightAttenuation1;

  vec3 lightColor2;
  vec3 lightPosition2;
  vec3 lightDirection2;
  vec3 lightAttenuation2;
} lighting;

PointLight lighting_getPointLight(int index) {
  switch (index) {
    case 0:
      return PointLight(lighting.lightColor0, lighting.lightPosition0, lighting.lightAttenuation0);
    case 1:
      return PointLight(lighting.lightColor1, lighting.lightPosition1, lighting.lightAttenuation1);
    case 2:
    default:  
      return PointLight(lighting.lightColor2, lighting.lightPosition2, lighting.lightAttenuation2);
  }
}

DirectionalLight lighting_getDirectionalLight(int index) {
  switch (index) {
    case 0:
      return DirectionalLight(lighting.lightColor0, lighting.lightDirection0);
    case 1:
      return DirectionalLight(lighting.lightColor1, lighting.lightDirection1);
    case 2:
    default:   
      return DirectionalLight(lighting.lightColor2, lighting.lightDirection2);
  }
} 

float getPointLightAttenuation(PointLight pointLight, float distance) {
  return pointLight.attenuation.x
       + pointLight.attenuation.y * distance
       + pointLight.attenuation.z * distance * distance;
}

// #endif
`,Qt=`// #if (defined(SHADER_TYPE_FRAGMENT) && defined(LIGHTING_FRAGMENT)) || (defined(SHADER_TYPE_VERTEX) && defined(LIGHTING_VERTEX))
struct AmbientLight {
  color: vec3<f32>,
};

struct PointLight {
  color: vec3<f32>,
  position: vec3<f32>,
  attenuation: vec3<f32>, // 2nd order x:Constant-y:Linear-z:Exponential
};

struct DirectionalLight {
  color: vec3<f32>,
  direction: vec3<f32>,
};

struct lightingUniforms {
  enabled: i32,
  pointLightCount: i32,
  directionalLightCount: i32,

  ambientColor: vec3<f32>,

  // TODO - support multiple lights by uncommenting arrays below
  lightType: i32,
  lightColor: vec3<f32>,
  lightDirection: vec3<f32>,
  lightPosition: vec3<f32>,
  lightAttenuation: vec3<f32>,

  // AmbientLight ambientLight;
  // PointLight pointLight[MAX_LIGHTS];
  // DirectionalLight directionalLight[MAX_LIGHTS];
};

// Binding 0:1 is reserved for lighting (Note: could go into separate bind group as it is stable across draw calls)
@binding(1) @group(0) var<uniform> lighting : lightingUniforms;

fn lighting_getPointLight(index: i32) -> PointLight {
  return PointLight(lighting.lightColor, lighting.lightPosition, lighting.lightAttenuation);
}

fn lighting_getDirectionalLight(index: i32) -> DirectionalLight {
  return DirectionalLight(lighting.lightColor, lighting.lightDirection);
} 

fn getPointLightAttenuation(pointLight: PointLight, distance: f32) -> f32 {
  return pointLight.attenuation.x
       + pointLight.attenuation.y * distance
       + pointLight.attenuation.z * distance * distance;
}
`,At=3,qt=255;var U;(function(o){o[o.POINT=0]="POINT",o[o.DIRECTIONAL=1]="DIRECTIONAL"})(U||(U={}));const J={props:{},uniforms:{},name:"lighting",defines:{MAX_LIGHTS:At},uniformTypes:{enabled:"i32",lightType:"i32",directionalLightCount:"i32",pointLightCount:"i32",ambientLightColor:"vec3<f32>",lightColor0:"vec3<f32>",lightPosition0:"vec3<f32>",lightDirection0:"vec3<f32>",lightAttenuation0:"vec3<f32>",lightColor1:"vec3<f32>",lightPosition1:"vec3<f32>",lightDirection1:"vec3<f32>",lightAttenuation1:"vec3<f32>",lightColor2:"vec3<f32>",lightPosition2:"vec3<f32>",lightDirection2:"vec3<f32>",lightAttenuation2:"vec3<f32>"},defaultUniforms:{enabled:1,lightType:U.POINT,directionalLightCount:0,pointLightCount:0,ambientLightColor:[.1,.1,.1],lightColor0:[1,1,1],lightPosition0:[1,1,2],lightDirection0:[1,1,1],lightAttenuation0:[1,0,0],lightColor1:[1,1,1],lightPosition1:[1,1,2],lightDirection1:[1,1,1],lightAttenuation1:[1,0,0],lightColor2:[1,1,1],lightPosition2:[1,1,2],lightDirection2:[1,1,1],lightAttenuation2:[1,0,0]},source:Qt,vs:xt,fs:xt,getUniforms:te};function te(o,i={}){if(o=o&&{...o},!o)return{...J.defaultUniforms};o.lights&&(o={...o,...ie(o.lights),lights:void 0});const{ambientLight:t,pointLights:r,directionalLights:a}=o||{};if(!(t||r&&r.length>0||a&&a.length>0))return{...J.defaultUniforms,enabled:0};const c={...J.defaultUniforms,...i,...ee({ambientLight:t,pointLights:r,directionalLights:a})};return o.enabled!==void 0&&(c.enabled=o.enabled?1:0),c}function ee({ambientLight:o,pointLights:i=[],directionalLights:t=[]}){const r={};r.ambientLightColor=st(o);let a=0;for(const l of i){r.lightType=U.POINT;const c=a;r[`lightColor${c}`]=st(l),r[`lightPosition${c}`]=l.position,r[`lightAttenuation${c}`]=l.attenuation||[1,0,0],a++}for(const l of t){r.lightType=U.DIRECTIONAL;const c=a;r[`lightColor${c}`]=st(l),r[`lightDirection${c}`]=l.direction,a++}return a>At&&Xt.warn("MAX_LIGHTS exceeded")(),r.directionalLightCount=t.length,r.pointLightCount=i.length,r}function ie(o){const i={pointLights:[],directionalLights:[]};for(const t of o||[])switch(t.type){case"ambient":i.ambientLight=t;break;case"directional":i.directionalLights?.push(t);break;case"point":i.pointLights?.push(t);break}return i}function st(o={}){const{color:i=[0,0,0],intensity:t=1}=o;return i.map(r=>r*t/qt)}const oe=`uniform phongMaterialUniforms {
  uniform float ambient;
  uniform float diffuse;
  uniform float shininess;
  uniform vec3  specularColor;
} material;
`,ne=`uniform phongMaterialUniforms {
  uniform float ambient;
  uniform float diffuse;
  uniform float shininess;
  uniform vec3  specularColor;
} material;

vec3 lighting_getLightColor(vec3 surfaceColor, vec3 light_direction, vec3 view_direction, vec3 normal_worldspace, vec3 color) {
  vec3 halfway_direction = normalize(light_direction + view_direction);
  float lambertian = dot(light_direction, normal_worldspace);
  float specular = 0.0;
  if (lambertian > 0.0) {
    float specular_angle = max(dot(normal_worldspace, halfway_direction), 0.0);
    specular = pow(specular_angle, material.shininess);
  }
  lambertian = max(lambertian, 0.0);
  return (lambertian * material.diffuse * surfaceColor + specular * material.specularColor) * color;
}

vec3 lighting_getLightColor(vec3 surfaceColor, vec3 cameraPosition, vec3 position_worldspace, vec3 normal_worldspace) {
  vec3 lightColor = surfaceColor;

  if (lighting.enabled == 0) {
    return lightColor;
  }

  vec3 view_direction = normalize(cameraPosition - position_worldspace);
  lightColor = material.ambient * surfaceColor * lighting.ambientColor;

  for (int i = 0; i < lighting.pointLightCount; i++) {
    PointLight pointLight = lighting_getPointLight(i);
    vec3 light_position_worldspace = pointLight.position;
    vec3 light_direction = normalize(light_position_worldspace - position_worldspace);
    float light_attenuation = getPointLightAttenuation(pointLight, distance(light_position_worldspace, position_worldspace));
    lightColor += lighting_getLightColor(surfaceColor, light_direction, view_direction, normal_worldspace, pointLight.color / light_attenuation);
  }

  int totalLights = min(MAX_LIGHTS, lighting.pointLightCount + lighting.directionalLightCount);
  for (int i = lighting.pointLightCount; i < totalLights; i++) {
    DirectionalLight directionalLight = lighting_getDirectionalLight(i);
    lightColor += lighting_getLightColor(surfaceColor, -directionalLight.direction, view_direction, normal_worldspace, directionalLight.color);
  }
  
  return lightColor;
}
`,re=`struct phongMaterialUniforms {
  ambient: f32,
  diffuse: f32,
  shininess: f32,
  specularColor: vec3<f32>,
};

@binding(2) @group(0) var<uniform> phongMaterial : phongMaterialUniforms;

fn lighting_getLightColor(surfaceColor: vec3<f32>, light_direction: vec3<f32>, view_direction: vec3<f32>, normal_worldspace: vec3<f32>, color: vec3<f32>) -> vec3<f32> {
  let halfway_direction: vec3<f32> = normalize(light_direction + view_direction);
  var lambertian: f32 = dot(light_direction, normal_worldspace);
  var specular: f32 = 0.0;
  if (lambertian > 0.0) {
    let specular_angle = max(dot(normal_worldspace, halfway_direction), 0.0);
    specular = pow(specular_angle, phongMaterial.shininess);
  }
  lambertian = max(lambertian, 0.0);
  return (lambertian * phongMaterial.diffuse * surfaceColor + specular * phongMaterial.specularColor) * color;
}

fn lighting_getLightColor2(surfaceColor: vec3<f32>, cameraPosition: vec3<f32>, position_worldspace: vec3<f32>, normal_worldspace: vec3<f32>) -> vec3<f32> {
  var lightColor: vec3<f32> = surfaceColor;

  if (lighting.enabled == 0) {
    return lightColor;
  }

  let view_direction: vec3<f32> = normalize(cameraPosition - position_worldspace);
  lightColor = phongMaterial.ambient * surfaceColor * lighting.ambientColor;

  if (lighting.lightType == 0) {
    let pointLight: PointLight  = lighting_getPointLight(0);
    let light_position_worldspace: vec3<f32> = pointLight.position;
    let light_direction: vec3<f32> = normalize(light_position_worldspace - position_worldspace);
    lightColor += lighting_getLightColor(surfaceColor, light_direction, view_direction, normal_worldspace, pointLight.color);
  } else if (lighting.lightType == 1) {
    var directionalLight: DirectionalLight = lighting_getDirectionalLight(0);
    lightColor += lighting_getLightColor(surfaceColor, -directionalLight.direction, view_direction, normal_worldspace, directionalLight.color);
  }
  
  return lightColor;
  /*
  for (int i = 0; i < MAX_LIGHTS; i++) {
    if (i >= lighting.pointLightCount) {
      break;
    }
    PointLight pointLight = lighting.pointLight[i];
    vec3 light_position_worldspace = pointLight.position;
    vec3 light_direction = normalize(light_position_worldspace - position_worldspace);
    lightColor += lighting_getLightColor(surfaceColor, light_direction, view_direction, normal_worldspace, pointLight.color);
  }

  for (int i = 0; i < MAX_LIGHTS; i++) {
    if (i >= lighting.directionalLightCount) {
      break;
    }
    DirectionalLight directionalLight = lighting.directionalLight[i];
    lightColor += lighting_getLightColor(surfaceColor, -directionalLight.direction, view_direction, normal_worldspace, directionalLight.color);
  }
  */
}

fn lighting_getSpecularLightColor(cameraPosition: vec3<f32>, position_worldspace: vec3<f32>, normal_worldspace: vec3<f32>) -> vec3<f32>{
  var lightColor = vec3<f32>(0, 0, 0);
  let surfaceColor = vec3<f32>(0, 0, 0);

  if (lighting.enabled == 0) {
    let view_direction = normalize(cameraPosition - position_worldspace);

    switch (lighting.lightType) {
      case 0, default: {
        let pointLight: PointLight = lighting_getPointLight(0);
        let light_position_worldspace: vec3<f32> = pointLight.position;
        let light_direction: vec3<f32> = normalize(light_position_worldspace - position_worldspace);
        lightColor += lighting_getLightColor(surfaceColor, light_direction, view_direction, normal_worldspace, pointLight.color);
      }
      case 1: {
        let directionalLight: DirectionalLight = lighting_getDirectionalLight(0);
        lightColor += lighting_getLightColor(surfaceColor, -directionalLight.direction, view_direction, normal_worldspace, directionalLight.color);
      }
    }
  }
  return lightColor;
}
`,It={props:{},name:"gouraudMaterial",vs:ne.replace("phongMaterial","gouraudMaterial"),fs:oe.replace("phongMaterial","gouraudMaterial"),source:re.replaceAll("phongMaterial","gouraudMaterial"),defines:{LIGHTING_VERTEX:1},dependencies:[J],uniformTypes:{ambient:"f32",diffuse:"f32",shininess:"f32",specularColor:"vec3<f32>"},defaultUniforms:{ambient:.35,diffuse:.6,shininess:32,specularColor:[.15,.15,.15]},getUniforms(o){const i={...o};return i.specularColor&&(i.specularColor=i.specularColor.map(t=>t/255)),{...It.defaultUniforms,...i}}},Mt={CLOCKWISE:1,COUNTER_CLOCKWISE:-1};function Et(o,i,t={}){return se(o,t)!==i?(ae(o,t),!0):!1}function se(o,i={}){return Math.sign(le(o,i))}const vt={x:0,y:1,z:2};function le(o,i={}){const{start:t=0,end:r=o.length,plane:a="xy"}=i,l=i.size||2;let c=0;const h=vt[a[0]],p=vt[a[1]];for(let x=t,m=r-l;x<r;x+=l)c+=(o[x+h]-o[m+h])*(o[x+p]+o[m+p]),m=x;return c/2}function ae(o,i){const{start:t=0,end:r=o.length,size:a=2}=i,l=(r-t)/a,c=Math.floor(l/2);for(let h=0;h<c;++h){const p=t+h*a,x=t+(l-1-h)*a;for(let m=0;m<a;++m){const P=o[p+m];o[p+m]=o[x+m],o[x+m]=P}}}var Z={exports:{}},Lt;function ce(){if(Lt)return Z.exports;Lt=1,Z.exports=o,Z.exports.default=o;function o(e,s,n){n=n||2;var g=s&&s.length,u=g?s[0]*n:e.length,f=i(e,0,u,n,!0),d=[];if(!f||f.next===f.prev)return d;var y,L,v,I,S,C,M;if(g&&(f=p(e,s,f,n)),e.length>80*n){y=v=e[0],L=I=e[1];for(var T=n;T<u;T+=n)S=e[T],C=e[T+1],S<y&&(y=S),C<L&&(L=C),S>v&&(v=S),C>I&&(I=C);M=Math.max(v-y,I-L),M=M!==0?32767/M:0}return r(f,d,n,y,L,M,0),d}function i(e,s,n,g,u){var f,d;if(u===ot(e,s,n,g)>0)for(f=s;f<n;f+=g)d=ft(f,e[f],e[f+1],d);else for(f=n-g;f>=s;f-=g)d=ft(f,e[f],e[f+1],d);return d&&V(d,d.next)&&(D(d),d=d.next),d}function t(e,s){if(!e)return e;s||(s=e);var n=e,g;do if(g=!1,!n.steiner&&(V(n,n.next)||A(n.prev,n,n.next)===0)){if(D(n),n=s=n.prev,n===n.next)break;g=!0}else n=n.next;while(g||n!==s);return s}function r(e,s,n,g,u,f,d){if(e){!d&&f&&O(e,g,u,f);for(var y=e,L,v;e.prev!==e.next;){if(L=e.prev,v=e.next,f?l(e,g,u,f):a(e)){s.push(L.i/n|0),s.push(e.i/n|0),s.push(v.i/n|0),D(e),e=v.next,y=v.next;continue}if(e=v,e===y){d?d===1?(e=c(t(e),s,n),r(e,s,n,g,u,f,2)):d===2&&h(e,s,n,g,u,f):r(t(e),s,n,g,u,f,1);break}}}}function a(e){var s=e.prev,n=e,g=e.next;if(A(s,n,g)>=0)return!1;for(var u=s.x,f=n.x,d=g.x,y=s.y,L=n.y,v=g.y,I=u<f?u<d?u:d:f<d?f:d,S=y<L?y<v?y:v:L<v?L:v,C=u>f?u>d?u:d:f>d?f:d,M=y>L?y>v?y:v:L>v?L:v,T=g.next;T!==s;){if(T.x>=I&&T.x<=C&&T.y>=S&&T.y<=M&&z(u,y,f,L,d,v,T.x,T.y)&&A(T.prev,T,T.next)>=0)return!1;T=T.next}return!0}function l(e,s,n,g){var u=e.prev,f=e,d=e.next;if(A(u,f,d)>=0)return!1;for(var y=u.x,L=f.x,v=d.x,I=u.y,S=f.y,C=d.y,M=y<L?y<v?y:v:L<v?L:v,T=I<S?I<C?I:C:S<C?S:C,G=y>L?y>v?y:v:L>v?L:v,N=I>S?I>C?I:C:S>C?S:C,dt=et(M,T,s,n,g),pt=et(G,N,s,n,g),_=e.prevZ,w=e.nextZ;_&&_.z>=dt&&w&&w.z<=pt;){if(_.x>=M&&_.x<=G&&_.y>=T&&_.y<=N&&_!==u&&_!==d&&z(y,I,L,S,v,C,_.x,_.y)&&A(_.prev,_,_.next)>=0||(_=_.prevZ,w.x>=M&&w.x<=G&&w.y>=T&&w.y<=N&&w!==u&&w!==d&&z(y,I,L,S,v,C,w.x,w.y)&&A(w.prev,w,w.next)>=0))return!1;w=w.nextZ}for(;_&&_.z>=dt;){if(_.x>=M&&_.x<=G&&_.y>=T&&_.y<=N&&_!==u&&_!==d&&z(y,I,L,S,v,C,_.x,_.y)&&A(_.prev,_,_.next)>=0)return!1;_=_.prevZ}for(;w&&w.z<=pt;){if(w.x>=M&&w.x<=G&&w.y>=T&&w.y<=N&&w!==u&&w!==d&&z(y,I,L,S,v,C,w.x,w.y)&&A(w.prev,w,w.next)>=0)return!1;w=w.nextZ}return!0}function c(e,s,n){var g=e;do{var u=g.prev,f=g.next.next;!V(u,f)&&ut(u,g,g.next,f)&&R(u,f)&&R(f,u)&&(s.push(u.i/n|0),s.push(g.i/n|0),s.push(f.i/n|0),D(g),D(g.next),g=e=f),g=g.next}while(g!==e);return t(g)}function h(e,s,n,g,u,f){var d=e;do{for(var y=d.next.next;y!==d.prev;){if(d.i!==y.i&&Gt(d,y)){var L=ht(d,y);d=t(d,d.next),L=t(L,L.next),r(d,s,n,g,u,f,0),r(L,s,n,g,u,f,0);return}y=y.next}d=d.next}while(d!==e)}function p(e,s,n,g){var u=[],f,d,y,L,v;for(f=0,d=s.length;f<d;f++)y=s[f]*g,L=f<d-1?s[f+1]*g:e.length,v=i(e,y,L,g,!1),v===v.next&&(v.steiner=!0),u.push(Dt(v));for(u.sort(x),f=0;f<u.length;f++)n=m(u[f],n);return n}function x(e,s){return e.x-s.x}function m(e,s){var n=P(e,s);if(!n)return s;var g=ht(n,e);return t(g,g.next),t(n,n.next)}function P(e,s){var n=s,g=e.x,u=e.y,f=-1/0,d;do{if(u<=n.y&&u>=n.next.y&&n.next.y!==n.y){var y=n.x+(u-n.y)*(n.next.x-n.x)/(n.next.y-n.y);if(y<=g&&y>f&&(f=y,d=n.x<n.next.x?n:n.next,y===g))return d}n=n.next}while(n!==s);if(!d)return null;var L=d,v=d.x,I=d.y,S=1/0,C;n=d;do g>=n.x&&n.x>=v&&g!==n.x&&z(u<I?g:f,u,v,I,u<I?f:g,u,n.x,n.y)&&(C=Math.abs(u-n.y)/(g-n.x),R(n,e)&&(C<S||C===S&&(n.x>d.x||n.x===d.x&&b(d,n)))&&(d=n,S=C)),n=n.next;while(n!==L);return d}function b(e,s){return A(e.prev,e,s.prev)<0&&A(s.next,e,e.next)<0}function O(e,s,n,g){var u=e;do u.z===0&&(u.z=et(u.x,u.y,s,n,g)),u.prevZ=u.prev,u.nextZ=u.next,u=u.next;while(u!==e);u.prevZ.nextZ=null,u.prevZ=null,tt(u)}function tt(e){var s,n,g,u,f,d,y,L,v=1;do{for(n=e,e=null,f=null,d=0;n;){for(d++,g=n,y=0,s=0;s<v&&(y++,g=g.nextZ,!!g);s++);for(L=v;y>0||L>0&&g;)y!==0&&(L===0||!g||n.z<=g.z)?(u=n,n=n.nextZ,y--):(u=g,g=g.nextZ,L--),f?f.nextZ=u:e=u,u.prevZ=f,f=u;n=g}f.nextZ=null,v*=2}while(d>1);return e}function et(e,s,n,g,u){return e=(e-n)*u|0,s=(s-g)*u|0,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,s=(s|s<<8)&16711935,s=(s|s<<4)&252645135,s=(s|s<<2)&858993459,s=(s|s<<1)&1431655765,e|s<<1}function Dt(e){var s=e,n=e;do(s.x<n.x||s.x===n.x&&s.y<n.y)&&(n=s),s=s.next;while(s!==e);return n}function z(e,s,n,g,u,f,d,y){return(u-d)*(s-y)>=(e-d)*(f-y)&&(e-d)*(g-y)>=(n-d)*(s-y)&&(n-d)*(f-y)>=(u-d)*(g-y)}function Gt(e,s){return e.next.i!==s.i&&e.prev.i!==s.i&&!Nt(e,s)&&(R(e,s)&&R(s,e)&&Ft(e,s)&&(A(e.prev,e,s.prev)||A(e,s.prev,s))||V(e,s)&&A(e.prev,e,e.next)>0&&A(s.prev,s,s.next)>0)}function A(e,s,n){return(s.y-e.y)*(n.x-s.x)-(s.x-e.x)*(n.y-s.y)}function V(e,s){return e.x===s.x&&e.y===s.y}function ut(e,s,n,g){var u=H(A(e,s,n)),f=H(A(e,s,g)),d=H(A(n,g,e)),y=H(A(n,g,s));return!!(u!==f&&d!==y||u===0&&B(e,n,s)||f===0&&B(e,g,s)||d===0&&B(n,e,g)||y===0&&B(n,s,g))}function B(e,s,n){return s.x<=Math.max(e.x,n.x)&&s.x>=Math.min(e.x,n.x)&&s.y<=Math.max(e.y,n.y)&&s.y>=Math.min(e.y,n.y)}function H(e){return e>0?1:e<0?-1:0}function Nt(e,s){var n=e;do{if(n.i!==e.i&&n.next.i!==e.i&&n.i!==s.i&&n.next.i!==s.i&&ut(n,n.next,e,s))return!0;n=n.next}while(n!==e);return!1}function R(e,s){return A(e.prev,e,e.next)<0?A(e,s,e.next)>=0&&A(e,e.prev,s)>=0:A(e,s,e.prev)<0||A(e,e.next,s)<0}function Ft(e,s){var n=e,g=!1,u=(e.x+s.x)/2,f=(e.y+s.y)/2;do n.y>f!=n.next.y>f&&n.next.y!==n.y&&u<(n.next.x-n.x)*(f-n.y)/(n.next.y-n.y)+n.x&&(g=!g),n=n.next;while(n!==e);return g}function ht(e,s){var n=new it(e.i,e.x,e.y),g=new it(s.i,s.x,s.y),u=e.next,f=s.prev;return e.next=s,s.prev=e,n.next=u,u.prev=n,g.next=n,n.prev=g,f.next=g,g.prev=f,g}function ft(e,s,n,g){var u=new it(e,s,n);return g?(u.next=g.next,u.prev=g,g.next.prev=u,g.next=u):(u.prev=u,u.next=u),u}function D(e){e.next.prev=e.prev,e.prev.next=e.next,e.prevZ&&(e.prevZ.nextZ=e.nextZ),e.nextZ&&(e.nextZ.prevZ=e.prevZ)}function it(e,s,n){this.i=e,this.x=s,this.y=n,this.prev=null,this.next=null,this.z=0,this.prevZ=null,this.nextZ=null,this.steiner=!1}o.deviation=function(e,s,n,g){var u=s&&s.length,f=u?s[0]*n:e.length,d=Math.abs(ot(e,0,f,n));if(u)for(var y=0,L=s.length;y<L;y++){var v=s[y]*n,I=y<L-1?s[y+1]*n:e.length;d-=Math.abs(ot(e,v,I,n))}var S=0;for(y=0;y<g.length;y+=3){var C=g[y]*n,M=g[y+1]*n,T=g[y+2]*n;S+=Math.abs((e[C]-e[T])*(e[M+1]-e[C+1])-(e[C]-e[M])*(e[T+1]-e[C+1]))}return d===0&&S===0?0:Math.abs((S-d)/d)};function ot(e,s,n,g){for(var u=0,f=s,d=n-g;f<n;f+=g)u+=(e[d]-e[f])*(e[f+1]+e[d+1]),d=f;return u}return o.flatten=function(e){for(var s=e[0][0].length,n={vertices:[],holes:[],dimensions:s},g=0,u=0;u<e.length;u++){for(var f=0;f<e[u].length;f++)for(var d=0;d<s;d++)n.vertices.push(e[u][f][d]);u>0&&(g+=e[u-1].length,n.holes.push(g))}return n},Z.exports}var ge=ce();const ue=jt(ge),$=Mt.CLOCKWISE,mt=Mt.COUNTER_CLOCKWISE,E={};function he(o){if(o=o&&o.positions||o,!Array.isArray(o)&&!ArrayBuffer.isView(o))throw new Error("invalid polygon")}function k(o){return"positions"in o?o.positions:o}function K(o){return"holeIndices"in o?o.holeIndices:null}function fe(o){return Array.isArray(o[0])}function de(o){return o.length>=1&&o[0].length>=2&&Number.isFinite(o[0][0])}function pe(o){const i=o[0],t=o[o.length-1];return i[0]===t[0]&&i[1]===t[1]&&i[2]===t[2]}function ye(o,i,t,r){for(let a=0;a<i;a++)if(o[t+a]!==o[r-i+a])return!1;return!0}function Pt(o,i,t,r,a){let l=i;const c=t.length;for(let h=0;h<c;h++)for(let p=0;p<r;p++)o[l++]=t[h][p]||0;if(!pe(t))for(let h=0;h<r;h++)o[l++]=t[0][h]||0;return E.start=i,E.end=l,E.size=r,Et(o,a,E),l}function Ct(o,i,t,r,a=0,l,c){l=l||t.length;const h=l-a;if(h<=0)return i;let p=i;for(let x=0;x<h;x++)o[p++]=t[a+x];if(!ye(t,r,a,l))for(let x=0;x<r;x++)o[p++]=t[a+x];return E.start=i,E.end=p,E.size=r,Et(o,c,E),p}function xe(o,i){he(o);const t=[],r=[];if("positions"in o){const{positions:a,holeIndices:l}=o;if(l){let c=0;for(let h=0;h<=l.length;h++)c=Ct(t,c,a,i,l[h-1],l[h],h===0?$:mt),r.push(c);return r.pop(),{positions:t,holeIndices:r}}o=a}if(!fe(o))return Ct(t,0,o,i,0,t.length,$),t;if(!de(o)){let a=0;for(const[l,c]of o.entries())a=Pt(t,a,c,i,l===0?$:mt),r.push(a);return r.pop(),{positions:t,holeIndices:r}}return Pt(t,0,o,i,$),t}function lt(o,i,t){const r=o.length/3;let a=0;for(let l=0;l<r;l++){const c=(l+1)%r;a+=o[l*3+i]*o[c*3+t],a-=o[c*3+i]*o[l*3+t]}return Math.abs(a/2)}function _t(o,i,t,r){const a=o.length/3;for(let l=0;l<a;l++){const c=l*3,h=o[c+0],p=o[c+1],x=o[c+2];o[c+i]=h,o[c+t]=p,o[c+r]=x}}function ve(o,i,t,r){let a=K(o);a&&(a=a.map(h=>h/i));let l=k(o);const c=r&&i===3;if(t){const h=l.length;l=l.slice();const p=[];for(let x=0;x<h;x+=i){p[0]=l[x],p[1]=l[x+1],c&&(p[2]=l[x+2]);const m=t(p);l[x]=m[0],l[x+1]=m[1],c&&(l[x+2]=m[2])}}if(c){const h=lt(l,0,1),p=lt(l,0,2),x=lt(l,1,2);if(!h&&!p&&!x)return[];h>p&&h>x||(p>x?(t||(l=l.slice()),_t(l,0,2,1)):(t||(l=l.slice()),_t(l,2,0,1)))}return ue(l,a,i)}class Le extends Bt{constructor(i){const{fp64:t,IndexType:r=Uint32Array}=i;super({...i,attributes:{positions:{size:3,type:t?Float64Array:Float32Array},vertexValid:{type:Uint16Array,size:1},indices:{type:r,size:1}}})}get(i){const{attributes:t}=this;return i==="indices"?t.indices&&t.indices.subarray(0,this.vertexCount):t[i]}updateGeometry(i){super.updateGeometry(i);const t=this.buffers.indices;if(t)this.vertexCount=(t.value||t).length;else if(this.data&&!this.getGeometry)throw new Error("missing indices buffer")}normalizeGeometry(i){if(this.normalize){const t=xe(i,this.positionSize);return this.opts.resolution?Ht(k(t),K(t),{size:this.positionSize,gridResolution:this.opts.resolution,edgeTypes:!0}):this.opts.wrapLongitude?Zt(k(t),K(t),{size:this.positionSize,maxLatitude:86,edgeTypes:!0}):t}return i}getGeometrySize(i){if(wt(i)){let t=0;for(const r of i)t+=this.getGeometrySize(r);return t}return k(i).length/this.positionSize}getGeometryFromBuffer(i){return this.normalize||!this.buffers.indices?super.getGeometryFromBuffer(i):null}updateGeometryAttributes(i,t){if(i&&wt(i))for(const r of i){const a=this.getGeometrySize(r);t.geometrySize=a,this.updateGeometryAttributes(r,t),t.vertexStart+=a,t.indexStart=this.indexStarts[t.geometryIndex+1]}else{const r=i;this._updateIndices(r,t),this._updatePositions(r,t),this._updateVertexValid(r,t)}}_updateIndices(i,{geometryIndex:t,vertexStart:r,indexStart:a}){const{attributes:l,indexStarts:c,typedArrayManager:h}=this;let p=l.indices;if(!p||!i)return;let x=a;const m=ve(i,this.positionSize,this.opts.preproject,this.opts.full3d);p=h.allocate(p,a+m.length,{copy:!0});for(let P=0;P<m.length;P++)p[x++]=m[P]+r;c[t+1]=a+m.length,l.indices=p}_updatePositions(i,{vertexStart:t,geometrySize:r}){const{attributes:{positions:a},positionSize:l}=this;if(!a||!i)return;const c=k(i);for(let h=t,p=0;p<r;h++,p++){const x=c[p*l],m=c[p*l+1],P=l>2?c[p*l+2]:0;a[h*3]=x,a[h*3+1]=m,a[h*3+2]=P}}_updateVertexValid(i,{vertexStart:t,geometrySize:r}){const{positionSize:a}=this,l=this.attributes.vertexValid,c=i&&K(i);if(i&&i.edgeTypes?l.set(i.edgeTypes,t):l.fill(1,t,t+r),c)for(let h=0;h<c.length;h++)l[t+c[h]/a-1]=0;l[t+r-1]=0}}function wt(o){return Array.isArray(o)&&o.length>0&&!Number.isFinite(o[0])}const bt=`uniform solidPolygonUniforms {
  bool extruded;
  bool isWireframe;
  float elevationScale;
} solidPolygon;
`,me={name:"solidPolygon",vs:bt,fs:bt,uniformTypes:{extruded:"f32",isWireframe:"f32",elevationScale:"f32"}},zt=`in vec4 fillColors;
in vec4 lineColors;
in vec3 pickingColors;
out vec4 vColor;
struct PolygonProps {
vec3 positions;
vec3 positions64Low;
vec3 normal;
float elevations;
};
vec3 project_offset_normal(vec3 vector) {
if (project.coordinateSystem == COORDINATE_SYSTEM_LNGLAT ||
project.coordinateSystem == COORDINATE_SYSTEM_LNGLAT_OFFSETS) {
return normalize(vector * project.commonUnitsPerWorldUnit);
}
return project_normal(vector);
}
void calculatePosition(PolygonProps props) {
vec3 pos = props.positions;
vec3 pos64Low = props.positions64Low;
vec3 normal = props.normal;
vec4 colors = solidPolygon.isWireframe ? lineColors : fillColors;
geometry.worldPosition = props.positions;
geometry.pickingColor = pickingColors;
if (solidPolygon.extruded) {
pos.z += props.elevations * solidPolygon.elevationScale;
}
gl_Position = project_position_to_clipspace(pos, pos64Low, vec3(0.), geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
if (solidPolygon.extruded) {
#ifdef IS_SIDE_VERTEX
normal = project_offset_normal(normal);
#else
normal = project_normal(normal);
#endif
geometry.normal = normal;
vec3 lightColor = lighting_getLightColor(colors.rgb, project.cameraPosition, geometry.position.xyz, geometry.normal);
vColor = vec4(lightColor, colors.a * layer.opacity);
} else {
vColor = vec4(colors.rgb, colors.a * layer.opacity);
}
DECKGL_FILTER_COLOR(vColor, geometry);
}
`,Pe=`#version 300 es
#define SHADER_NAME solid-polygon-layer-vertex-shader
in vec3 vertexPositions;
in vec3 vertexPositions64Low;
in float elevations;
${zt}
void main(void) {
PolygonProps props;
props.positions = vertexPositions;
props.positions64Low = vertexPositions64Low;
props.elevations = elevations;
props.normal = vec3(0.0, 0.0, 1.0);
calculatePosition(props);
}
`,Ce=`#version 300 es
#define SHADER_NAME solid-polygon-layer-vertex-shader-side
#define IS_SIDE_VERTEX
in vec2 positions;
in vec3 vertexPositions;
in vec3 nextVertexPositions;
in vec3 vertexPositions64Low;
in vec3 nextVertexPositions64Low;
in float elevations;
in float instanceVertexValid;
${zt}
void main(void) {
if(instanceVertexValid < 0.5){
gl_Position = vec4(0.);
return;
}
PolygonProps props;
vec3 pos;
vec3 pos64Low;
vec3 nextPos;
vec3 nextPos64Low;
#if RING_WINDING_ORDER_CW == 1
pos = vertexPositions;
pos64Low = vertexPositions64Low;
nextPos = nextVertexPositions;
nextPos64Low = nextVertexPositions64Low;
#else
pos = nextVertexPositions;
pos64Low = nextVertexPositions64Low;
nextPos = vertexPositions;
nextPos64Low = vertexPositions64Low;
#endif
props.positions = mix(pos, nextPos, positions.x);
props.positions64Low = mix(pos64Low, nextPos64Low, positions.x);
props.normal = vec3(
pos.y - nextPos.y + (pos64Low.y - nextPos64Low.y),
nextPos.x - pos.x + (nextPos64Low.x - pos64Low.x),
0.0);
props.elevations = elevations * positions.y;
calculatePosition(props);
}
`,_e=`#version 300 es
#define SHADER_NAME solid-polygon-layer-fragment-shader
precision highp float;
in vec4 vColor;
out vec4 fragColor;
void main(void) {
fragColor = vColor;
geometry.uv = vec2(0.);
DECKGL_FILTER_COLOR(fragColor, geometry);
}
`,q=[0,0,0,255],we={filled:!0,extruded:!1,wireframe:!1,_normalize:!0,_windingOrder:"CW",_full3d:!1,elevationScale:{type:"number",min:0,value:1},getPolygon:{type:"accessor",value:o=>o.polygon},getElevation:{type:"accessor",value:1e3},getFillColor:{type:"accessor",value:q},getLineColor:{type:"accessor",value:q},material:!0},j={enter:(o,i)=>i.length?i.subarray(i.length-o.length):o};class gt extends Jt{getShaders(i){return super.getShaders({vs:i==="top"?Pe:Ce,fs:_e,defines:{RING_WINDING_ORDER_CW:!this.props._normalize&&this.props._windingOrder==="CCW"?0:1},modules:[Kt,It,Yt,me]})}get wrapLongitude(){return!1}getBounds(){return this.getAttributeManager()?.getBounds(["vertexPositions"])}initializeState(){const{viewport:i}=this.context;let{coordinateSystem:t}=this.props;const{_full3d:r}=this.props;i.isGeospatial&&t===nt.DEFAULT&&(t=nt.LNGLAT);let a;t===nt.LNGLAT&&(r?a=i.projectPosition.bind(i):a=i.projectFlat.bind(i)),this.setState({numInstances:0,polygonTesselator:new Le({preproject:a,fp64:this.use64bitPositions(),IndexType:Uint32Array})});const l=this.getAttributeManager(),c=!0;l.remove(["instancePickingColors"]),l.add({indices:{size:1,isIndexed:!0,update:this.calculateIndices,noAlloc:c},vertexPositions:{size:3,type:"float64",stepMode:"dynamic",fp64:this.use64bitPositions(),transition:j,accessor:"getPolygon",update:this.calculatePositions,noAlloc:c,shaderAttributes:{nextVertexPositions:{vertexOffset:1}}},instanceVertexValid:{size:1,type:"uint16",stepMode:"instance",update:this.calculateVertexValid,noAlloc:c},elevations:{size:1,stepMode:"dynamic",transition:j,accessor:"getElevation"},fillColors:{size:this.props.colorFormat.length,type:"unorm8",stepMode:"dynamic",transition:j,accessor:"getFillColor",defaultValue:q},lineColors:{size:this.props.colorFormat.length,type:"unorm8",stepMode:"dynamic",transition:j,accessor:"getLineColor",defaultValue:q},pickingColors:{size:4,type:"uint8",stepMode:"dynamic",accessor:(h,{index:p,target:x})=>this.encodePickingColor(h&&h.__source?h.__source.index:p,x)}})}getPickingInfo(i){const t=super.getPickingInfo(i),{index:r}=t,a=this.props.data;return a[0]&&a[0].__source&&(t.object=a.find(l=>l.__source.index===r)),t}disablePickingIndex(i){const t=this.props.data;if(t[0]&&t[0].__source)for(let r=0;r<t.length;r++)t[r].__source.index===i&&this._disablePickingIndex(r);else super.disablePickingIndex(i)}draw({uniforms:i}){const{extruded:t,filled:r,wireframe:a,elevationScale:l}=this.props,{topModel:c,sideModel:h,wireframeModel:p,polygonTesselator:x}=this.state,m={extruded:!!t,elevationScale:l,isWireframe:!1};p&&a&&(p.setInstanceCount(x.instanceCount-1),p.shaderInputs.setProps({solidPolygon:{...m,isWireframe:!0}}),p.draw(this.context.renderPass)),h&&r&&(h.setInstanceCount(x.instanceCount-1),h.shaderInputs.setProps({solidPolygon:m}),h.draw(this.context.renderPass)),c&&r&&(c.setVertexCount(x.vertexCount),c.shaderInputs.setProps({solidPolygon:m}),c.draw(this.context.renderPass))}updateState(i){super.updateState(i),this.updateGeometry(i);const{props:t,oldProps:r,changeFlags:a}=i,l=this.getAttributeManager();(a.extensionsChanged||t.filled!==r.filled||t.extruded!==r.extruded)&&(this.state.models?.forEach(h=>h.destroy()),this.setState(this._getModels()),l.invalidateAll())}updateGeometry({props:i,oldProps:t,changeFlags:r}){if(r.dataChanged||r.updateTriggersChanged&&(r.updateTriggersChanged.all||r.updateTriggersChanged.getPolygon)){const{polygonTesselator:l}=this.state,c=i.data.attributes||{};l.updateGeometry({data:i.data,normalize:i._normalize,geometryBuffer:c.getPolygon,buffers:c,getGeometry:i.getPolygon,positionFormat:i.positionFormat,wrapLongitude:i.wrapLongitude,resolution:this.context.viewport.resolution,fp64:this.use64bitPositions(),dataChanged:r.dataChanged,full3d:i._full3d}),this.setState({numInstances:l.instanceCount,startIndices:l.vertexStarts}),r.dataChanged||this.getAttributeManager().invalidateAll()}}_getModels(){const{id:i,filled:t,extruded:r}=this.props;let a,l,c;if(t){const h=this.getShaders("top");h.defines.NON_INSTANCED_MODEL=1;const p=this.getAttributeManager().getBufferLayouts({isInstanced:!1});a=new rt(this.context.device,{...h,id:`${i}-top`,topology:"triangle-list",bufferLayout:p,isIndexed:!0,userData:{excludeAttributes:{instanceVertexValid:!0}}})}if(r){const h=this.getAttributeManager().getBufferLayouts({isInstanced:!0});l=new rt(this.context.device,{...this.getShaders("side"),id:`${i}-side`,bufferLayout:h,geometry:new yt({topology:"triangle-strip",attributes:{positions:{size:2,value:new Float32Array([1,0,0,0,1,1,0,1])}}}),isInstanced:!0,userData:{excludeAttributes:{indices:!0}}}),c=new rt(this.context.device,{...this.getShaders("side"),id:`${i}-wireframe`,bufferLayout:h,geometry:new yt({topology:"line-strip",attributes:{positions:{size:2,value:new Float32Array([1,0,0,0,0,1,1,1])}}}),isInstanced:!0,userData:{excludeAttributes:{indices:!0}}})}return{models:[l,c,a].filter(Boolean),topModel:a,sideModel:l,wireframeModel:c}}calculateIndices(i){const{polygonTesselator:t}=this.state;i.startIndices=t.indexStarts,i.value=t.get("indices")}calculatePositions(i){const{polygonTesselator:t}=this.state;i.startIndices=t.vertexStarts,i.value=t.get("positions")}calculateVertexValid(i){i.value=this.state.polygonTesselator.get("vertexValid")}}gt.defaultProps=we;gt.layerName="SolidPolygonLayer";function be({data:o,getIndex:i,dataRange:t,replace:r}){const{startRow:a=0,endRow:l=1/0}=t,c=o.length;let h=c,p=c;for(let b=0;b<c;b++){const O=i(o[b]);if(h>b&&O>=a&&(h=b),O>=l){p=b;break}}let x=h;const P=p-h!==r.length?o.slice(p):void 0;for(let b=0;b<r.length;b++)o[x++]=r[b];if(P){for(let b=0;b<P.length;b++)o[x++]=P[b];o.length=x}return{startRow:h,endRow:h+r.length}}function Se(o,i){if(!o)return null;const t="startIndices"in o?o.startIndices[i]:i,r=o.featureIds.value[t];return t!==-1?Te(o,r,t):null}function Te(o,i,t){const r={properties:{...o.properties[i]}};for(const a in o.numericProps)r.properties[a]=o.numericProps[a].value[t];return r}function Ae(o,i){const t={points:null,lines:null,polygons:null};for(const r in t){const a=o[r].globalFeatureIds.value;t[r]=new Uint8ClampedArray(a.length*4);const l=[];for(let c=0;c<a.length;c++)i(a[c],l),t[r][c*4+0]=l[0],t[r][c*4+1]=l[1],t[r][c*4+2]=l[2],t[r][c*4+3]=255}return t}const Y={circle:{type:Ut,props:{filled:"filled",stroked:"stroked",lineWidthMaxPixels:"lineWidthMaxPixels",lineWidthMinPixels:"lineWidthMinPixels",lineWidthScale:"lineWidthScale",lineWidthUnits:"lineWidthUnits",pointRadiusMaxPixels:"radiusMaxPixels",pointRadiusMinPixels:"radiusMinPixels",pointRadiusScale:"radiusScale",pointRadiusUnits:"radiusUnits",pointAntialiasing:"antialiasing",pointBillboard:"billboard",getFillColor:"getFillColor",getLineColor:"getLineColor",getLineWidth:"getLineWidth",getPointRadius:"getRadius"}},icon:{type:Wt,props:{iconAtlas:"iconAtlas",iconMapping:"iconMapping",iconSizeMaxPixels:"sizeMaxPixels",iconSizeMinPixels:"sizeMinPixels",iconSizeScale:"sizeScale",iconSizeUnits:"sizeUnits",iconAlphaCutoff:"alphaCutoff",iconBillboard:"billboard",getIcon:"getIcon",getIconAngle:"getAngle",getIconColor:"getColor",getIconPixelOffset:"getPixelOffset",getIconSize:"getSize"}},text:{type:kt,props:{textSizeMaxPixels:"sizeMaxPixels",textSizeMinPixels:"sizeMinPixels",textSizeScale:"sizeScale",textSizeUnits:"sizeUnits",textBackground:"background",textBackgroundPadding:"backgroundPadding",textFontFamily:"fontFamily",textFontWeight:"fontWeight",textLineHeight:"lineHeight",textMaxWidth:"maxWidth",textOutlineColor:"outlineColor",textOutlineWidth:"outlineWidth",textWordBreak:"wordBreak",textCharacterSet:"characterSet",textBillboard:"billboard",textFontSettings:"fontSettings",getText:"getText",getTextAngle:"getAngle",getTextColor:"getColor",getTextPixelOffset:"getPixelOffset",getTextSize:"getSize",getTextAnchor:"getTextAnchor",getTextAlignmentBaseline:"getAlignmentBaseline",getTextBackgroundColor:"getBackgroundColor",getTextBorderColor:"getBorderColor",getTextBorderWidth:"getBorderWidth"}}},Q={type:$t,props:{lineWidthUnits:"widthUnits",lineWidthScale:"widthScale",lineWidthMinPixels:"widthMinPixels",lineWidthMaxPixels:"widthMaxPixels",lineJointRounded:"jointRounded",lineCapRounded:"capRounded",lineMiterLimit:"miterLimit",lineBillboard:"billboard",getLineColor:"getColor",getLineWidth:"getWidth"}},ct={type:gt,props:{extruded:"extruded",filled:"filled",wireframe:"wireframe",elevationScale:"elevationScale",material:"material",_full3d:"_full3d",getElevation:"getElevation",getFillColor:"getFillColor",getLineColor:"getLineColor"}};function F({type:o,props:i}){const t={};for(const r in i)t[r]=o.defaultProps[i[r]];return t}function at(o,i){const{transitions:t,updateTriggers:r}=o.props,a={updateTriggers:{},transitions:t&&{getPosition:t.geometry}};for(const l in i){const c=i[l];let h=o.props[l];l.startsWith("get")&&(h=o.getSubLayerAccessor(h),a.updateTriggers[c]=r[l],t&&(a.transitions[c]=t[l])),a[c]=h}return a}function Ie(o){if(Array.isArray(o))return o;switch(W.assert(o.type,"GeoJSON does not have type"),o.type){case"Feature":return[o];case"FeatureCollection":return W.assert(Array.isArray(o.features),"GeoJSON does not have features array"),o.features;default:return[{geometry:o}]}}function St(o,i,t={}){const r={pointFeatures:[],lineFeatures:[],polygonFeatures:[],polygonOutlineFeatures:[]},{startRow:a=0,endRow:l=o.length}=t;for(let c=a;c<l;c++){const h=o[c],{geometry:p}=h;if(p)if(p.type==="GeometryCollection"){W.assert(Array.isArray(p.geometries),"GeoJSON does not have geometries array");const{geometries:x}=p;for(let m=0;m<x.length;m++){const P=x[m];Tt(P,r,i,h,c)}}else Tt(p,r,i,h,c)}return r}function Tt(o,i,t,r,a){const{type:l,coordinates:c}=o,{pointFeatures:h,lineFeatures:p,polygonFeatures:x,polygonOutlineFeatures:m}=i;if(!Ee(l,c)){W.warn(`${l} coordinates are malformed`)();return}switch(l){case"Point":h.push(t({geometry:o},r,a));break;case"MultiPoint":c.forEach(P=>{h.push(t({geometry:{type:"Point",coordinates:P}},r,a))});break;case"LineString":p.push(t({geometry:o},r,a));break;case"MultiLineString":c.forEach(P=>{p.push(t({geometry:{type:"LineString",coordinates:P}},r,a))});break;case"Polygon":x.push(t({geometry:o},r,a)),c.forEach(P=>{m.push(t({geometry:{type:"LineString",coordinates:P}},r,a))});break;case"MultiPolygon":c.forEach(P=>{x.push(t({geometry:{type:"Polygon",coordinates:P}},r,a)),P.forEach(b=>{m.push(t({geometry:{type:"LineString",coordinates:b}},r,a))})});break}}const Me={Point:1,MultiPoint:2,LineString:2,MultiLineString:3,Polygon:3,MultiPolygon:4};function Ee(o,i){let t=Me[o];for(W.assert(t,`Unknown GeoJSON type ${o}`);i&&--t>0;)i=i[0];return i&&Number.isFinite(i[0])}function Ot(){return{points:{},lines:{},polygons:{},polygonsOutline:{}}}function X(o){return o.geometry.coordinates}function ze(o,i){const t=Ot(),{pointFeatures:r,lineFeatures:a,polygonFeatures:l,polygonOutlineFeatures:c}=o;return t.points.data=r,t.points._dataDiff=i.pointFeatures&&(()=>i.pointFeatures),t.points.getPosition=X,t.lines.data=a,t.lines._dataDiff=i.lineFeatures&&(()=>i.lineFeatures),t.lines.getPath=X,t.polygons.data=l,t.polygons._dataDiff=i.polygonFeatures&&(()=>i.polygonFeatures),t.polygons.getPolygon=X,t.polygonsOutline.data=c,t.polygonsOutline._dataDiff=i.polygonOutlineFeatures&&(()=>i.polygonOutlineFeatures),t.polygonsOutline.getPath=X,t}function Oe(o,i){const t=Ot(),{points:r,lines:a,polygons:l}=o,c=Ae(o,i);return t.points.data={length:r.positions.value.length/r.positions.size,attributes:{...r.attributes,getPosition:r.positions,instancePickingColors:{size:4,value:c.points}},properties:r.properties,numericProps:r.numericProps,featureIds:r.featureIds},t.lines.data={length:a.pathIndices.value.length-1,startIndices:a.pathIndices.value,attributes:{...a.attributes,getPath:a.positions,instancePickingColors:{size:4,value:c.lines}},properties:a.properties,numericProps:a.numericProps,featureIds:a.featureIds},t.lines._pathType="open",t.polygons.data={length:l.polygonIndices.value.length-1,startIndices:l.polygonIndices.value,attributes:{...l.attributes,getPolygon:l.positions,pickingColors:{size:4,value:c.polygons}},properties:l.properties,numericProps:l.numericProps,featureIds:l.featureIds},t.polygons._normalize=!1,l.triangles&&(t.polygons.data.attributes.indices=l.triangles.value),t.polygonsOutline.data={length:l.primitivePolygonIndices.value.length-1,startIndices:l.primitivePolygonIndices.value,attributes:{...l.attributes,getPath:l.positions,instancePickingColors:{size:4,value:c.polygons}},properties:l.properties,numericProps:l.numericProps,featureIds:l.featureIds},t.polygonsOutline._pathType="open",t}const Re=["points","linestrings","polygons"],De={...F(Y.circle),...F(Y.icon),...F(Y.text),...F(Q),...F(ct),stroked:!0,filled:!0,extruded:!1,wireframe:!1,_full3d:!1,iconAtlas:{type:"object",value:null},iconMapping:{type:"object",value:{}},getIcon:{type:"accessor",value:o=>o.properties.icon},getText:{type:"accessor",value:o=>o.properties.text},pointType:"circle",getRadius:{deprecatedFor:"getPointRadius"}};class Rt extends Vt{initializeState(){this.state={layerProps:{},features:{},featuresDiff:{}}}updateState({props:i,changeFlags:t}){if(!t.dataChanged)return;const{data:r}=this.props,a=r&&"points"in r&&"polygons"in r&&"lines"in r;this.setState({binary:a}),a?this._updateStateBinary({props:i,changeFlags:t}):this._updateStateJSON({props:i,changeFlags:t})}_updateStateBinary({props:i,changeFlags:t}){const r=Oe(i.data,this.encodePickingColor);this.setState({layerProps:r})}_updateStateJSON({props:i,changeFlags:t}){const r=Ie(i.data),a=this.getSubLayerRow.bind(this);let l={};const c={};if(Array.isArray(t.dataChanged)){const p=this.state.features;for(const x in p)l[x]=p[x].slice(),c[x]=[];for(const x of t.dataChanged){const m=St(r,a,x);for(const P in p)c[P].push(be({data:l[P],getIndex:b=>b.__source.index,dataRange:x,replace:m[P]}))}}else l=St(r,a);const h=ze(l,c);this.setState({features:l,featuresDiff:c,layerProps:h})}getPickingInfo(i){const t=super.getPickingInfo(i),{index:r,sourceLayer:a}=t;return t.featureType=Re.find(l=>a.id.startsWith(`${this.id}-${l}-`)),r>=0&&a.id.startsWith(`${this.id}-points-text`)&&this.state.binary&&(t.index=this.props.data.points.globalFeatureIds.value[r]),t}_updateAutoHighlight(i){const t=`${this.id}-points-`,r=i.featureType==="points";for(const a of this.getSubLayers())a.id.startsWith(t)===r&&a.updateAutoHighlight(i)}_renderPolygonLayer(){const{extruded:i,wireframe:t}=this.props,{layerProps:r}=this.state,a="polygons-fill",l=this.shouldRenderSubLayer(a,r.polygons?.data)&&this.getSubLayerClass(a,ct.type);if(l){const c=at(this,ct.props),h=i&&t;return h||delete c.getLineColor,c.updateTriggers.lineColors=h,new l(c,this.getSubLayerProps({id:a,updateTriggers:c.updateTriggers}),r.polygons)}return null}_renderLineLayers(){const{extruded:i,stroked:t}=this.props,{layerProps:r}=this.state,a="polygons-stroke",l="linestrings",c=!i&&t&&this.shouldRenderSubLayer(a,r.polygonsOutline?.data)&&this.getSubLayerClass(a,Q.type),h=this.shouldRenderSubLayer(l,r.lines?.data)&&this.getSubLayerClass(l,Q.type);if(c||h){const p=at(this,Q.props);return[c&&new c(p,this.getSubLayerProps({id:a,updateTriggers:p.updateTriggers}),r.polygonsOutline),h&&new h(p,this.getSubLayerProps({id:l,updateTriggers:p.updateTriggers}),r.lines)]}return null}_renderPointLayers(){const{pointType:i}=this.props,{layerProps:t,binary:r}=this.state;let{highlightedObjectIndex:a}=this.props;!r&&Number.isFinite(a)&&(a=t.points.data.findIndex(h=>h.__source.index===a));const l=new Set(i.split("+")),c=[];for(const h of l){const p=`points-${h}`,x=Y[h],m=x&&this.shouldRenderSubLayer(p,t.points?.data)&&this.getSubLayerClass(p,x.type);if(m){const P=at(this,x.props);let b=t.points;if(h==="text"&&r){const{instancePickingColors:O,...tt}=b.data.attributes;b={...b,data:{...b.data,attributes:tt}}}c.push(new m(P,this.getSubLayerProps({id:p,updateTriggers:P.updateTriggers,highlightedObjectIndex:a}),b))}}return c}renderLayers(){const{extruded:i}=this.props,t=this._renderPolygonLayer(),r=this._renderLineLayers(),a=this._renderPointLayers();return[!i&&t,r,a,i&&t]}getSubLayerAccessor(i){const{binary:t}=this.state;return!t||typeof i!="function"?super.getSubLayerAccessor(i):(r,a)=>{const{data:l,index:c}=a,h=Se(l,c);return i(h,a)}}}Rt.layerName="GeoJsonLayer";Rt.defaultProps=De;export{Rt as G,ne as P,gt as S,Mt as W,oe as a,re as b,We as c,It as g,J as l,Et as m};
