import"./_Uint8Array-CPNtPV0k.js";import"./_baseIsEqual-Colb33IN.js";import"./_arrayReduce-BnF2698I.js";import"./toNumber-D8Yr4jg3.js";import"./toInteger-HqbAY1oN.js";import"./isArrayLikeObject-VZQcF0wU.js";import"./_getTag-DAtegGfi.js";import"./_baseUniq-C9yRQ2gm.js";import"./chunk-4KMFLZZN-CY26YA_6.js";import"./_toKey-ySt2z-83.js";import"./memoize-Dkaig2Zu.js";import"./get-DpPiA0nD.js";import"./_baseFlatten-fXFruJ9c.js";import"./_basePickBy-ZofuMBT_.js";import"./merge-BK4jEs5n.js";import"./_baseSlice-Uxm09S3C.js";import"./clone-LWFvUGYK.js";import"./_baseEach-D9MoMllW.js";import"./hasIn-B8CzC4pq.js";import"./_baseProperty-DbWSe5Dg.js";import"./_createAggregator-DXVrFTZa.js";import"./min-DOP7dRSW.js";import"./_baseMap-DpEJo8vx.js";import"./isEmpty-CgS1RHPI.js";import"./_baseSet-DydOhF3e.js";import"./preload-helper-VwE_myu3.js";import"./main-Bhvb2Udf.js";import"./timer-BQp7kwGJ.js";import"./src-BxsaLGej.js";import"./math-CJPGrKXj.js";import"./step-CU2Y1mmF.js";import{i as v}from"./chunk-S3R3BYOJ-DkagUBh0.js";import{n as l,r as S}from"./src-BYP9eq-z.js";import{B as I,C as z,T as E,U as F,_ as P,a as R,d as D,v as B,y as w,z as G}from"./chunk-ABZYJK2D-CHn8e59f.js";import{t as V}from"./chunk-EXTU4WIE-BZKh82b1.js";import"./dist-DB8I7jQZ.js";import"./chunk-JEIROHC2-BY2EU-rF.js";import"./chunk-BN7GFLIU-DO5HMFB8.js";import"./chunk-T44TD3VJ-C0KWOLbc.js";import"./chunk-KMC2YHZD-Cj5sqkCw.js";import"./chunk-WFWHJNB7-ssq6vNBh.js";import"./chunk-WFRQ32O7-Dhkf3nPa.js";import"./chunk-XRWGC2XP-DOkbSHfa.js";import{t as _}from"./chunk-4BX2VUAB-CLo-a5yO.js";import{t as j}from"./mermaid-parser.core-BmfVzo1e.js";var u={showLegend:!0,ticks:5,max:null,min:0,graticule:"circle"},b={axes:[],curves:[],options:u},h=structuredClone(b),W=D.radar,H=l(()=>v({...W,...w().radar}),"getConfig"),C=l(()=>h.axes,"getAxes"),N=l(()=>h.curves,"getCurves"),U=l(()=>h.options,"getOptions"),Z=l(e=>{h.axes=e.map(t=>({name:t.name,label:t.label??t.name}))},"setAxes"),q=l(e=>{h.curves=e.map(t=>({name:t.name,label:t.label??t.name,entries:J(t.entries)}))},"setCurves"),J=l(e=>{if(e[0].axis==null)return e.map(r=>r.value);let t=C();if(t.length===0)throw Error("Axes must be populated before curves for reference entries");return t.map(r=>{let a=e.find(i=>{var s;return((s=i.axis)==null?void 0:s.$refText)===r.name});if(a===void 0)throw Error("Missing entry for axis "+r.label);return a.value})},"computeCurveEntries"),$={getAxes:C,getCurves:N,getOptions:U,setAxes:Z,setCurves:q,setOptions:l(e=>{var r,a,i,s,n;let t=e.reduce((o,p)=>(o[p.name]=p,o),{});h.options={showLegend:((r=t.showLegend)==null?void 0:r.value)??u.showLegend,ticks:((a=t.ticks)==null?void 0:a.value)??u.ticks,max:((i=t.max)==null?void 0:i.value)??u.max,min:((s=t.min)==null?void 0:s.value)??u.min,graticule:((n=t.graticule)==null?void 0:n.value)??u.graticule}},"setOptions"),getConfig:H,clear:l(()=>{R(),h=structuredClone(b)},"clear"),setAccTitle:I,getAccTitle:B,setDiagramTitle:F,getDiagramTitle:z,getAccDescription:P,setAccDescription:G},K=l(e=>{_(e,$);let{axes:t,curves:r,options:a}=e;$.setAxes(t),$.setCurves(r),$.setOptions(a)},"populate"),Q={parse:l(async e=>{let t=await j("radar",e);S.debug(t),K(t)},"parse")},X=l((e,t,r,a)=>{let i=a.db,s=i.getAxes(),n=i.getCurves(),o=i.getOptions(),p=i.getConfig(),d=i.getDiagramTitle(),c=V(t),m=Y(c,p),g=o.max??Math.max(...n.map(y=>Math.max(...y.entries))),x=o.min,f=Math.min(p.width,p.height)/2;tt(m,s,f,o.ticks,o.graticule),rt(m,s,f,p),M(m,s,n,x,g,o.graticule,p),A(m,n,o.showLegend,p),m.append("text").attr("class","radarTitle").text(d).attr("x",0).attr("y",-p.height/2-p.marginTop)},"draw"),Y=l((e,t)=>{let r=t.width+t.marginLeft+t.marginRight,a=t.height+t.marginTop+t.marginBottom,i={x:t.marginLeft+t.width/2,y:t.marginTop+t.height/2};return e.attr("viewbox",`0 0 ${r} ${a}`).attr("width",r).attr("height",a),e.append("g").attr("transform",`translate(${i.x}, ${i.y})`)},"drawFrame"),tt=l((e,t,r,a,i)=>{if(i==="circle")for(let s=0;s<a;s++){let n=r*(s+1)/a;e.append("circle").attr("r",n).attr("class","radarGraticule")}else if(i==="polygon"){let s=t.length;for(let n=0;n<a;n++){let o=r*(n+1)/a,p=t.map((d,c)=>{let m=2*c*Math.PI/s-Math.PI/2,g=o*Math.cos(m),x=o*Math.sin(m);return`${g},${x}`}).join(" ");e.append("polygon").attr("points",p).attr("class","radarGraticule")}}},"drawGraticule"),rt=l((e,t,r,a)=>{let i=t.length;for(let s=0;s<i;s++){let n=t[s].label,o=2*s*Math.PI/i-Math.PI/2;e.append("line").attr("x1",0).attr("y1",0).attr("x2",r*a.axisScaleFactor*Math.cos(o)).attr("y2",r*a.axisScaleFactor*Math.sin(o)).attr("class","radarAxisLine"),e.append("text").text(n).attr("x",r*a.axisLabelFactor*Math.cos(o)).attr("y",r*a.axisLabelFactor*Math.sin(o)).attr("class","radarAxisLabel")}},"drawAxes");function M(e,t,r,a,i,s,n){let o=t.length,p=Math.min(n.width,n.height)/2;r.forEach((d,c)=>{if(d.entries.length!==o)return;let m=d.entries.map((g,x)=>{let f=2*Math.PI*x/o-Math.PI/2,y=L(g,a,i,p),k=y*Math.cos(f),O=y*Math.sin(f);return{x:k,y:O}});s==="circle"?e.append("path").attr("d",T(m,n.curveTension)).attr("class",`radarCurve-${c}`):s==="polygon"&&e.append("polygon").attr("points",m.map(g=>`${g.x},${g.y}`).join(" ")).attr("class",`radarCurve-${c}`)})}l(M,"drawCurves");function L(e,t,r,a){return a*(Math.min(Math.max(e,t),r)-t)/(r-t)}l(L,"relativeRadius");function T(e,t){let r=e.length,a=`M${e[0].x},${e[0].y}`;for(let i=0;i<r;i++){let s=e[(i-1+r)%r],n=e[i],o=e[(i+1)%r],p=e[(i+2)%r],d={x:n.x+(o.x-s.x)*t,y:n.y+(o.y-s.y)*t},c={x:o.x-(p.x-n.x)*t,y:o.y-(p.y-n.y)*t};a+=` C${d.x},${d.y} ${c.x},${c.y} ${o.x},${o.y}`}return`${a} Z`}l(T,"closedRoundCurve");function A(e,t,r,a){if(!r)return;let i=(a.width/2+a.marginRight)*3/4,s=-(a.height/2+a.marginTop)*3/4;t.forEach((n,o)=>{let p=e.append("g").attr("transform",`translate(${i}, ${s+o*20})`);p.append("rect").attr("width",12).attr("height",12).attr("class",`radarLegendBox-${o}`),p.append("text").attr("x",16).attr("y",0).attr("class","radarLegendText").text(n.label)})}l(A,"drawLegend");var et={draw:X},at=l((e,t)=>{let r="";for(let a=0;a<e.THEME_COLOR_LIMIT;a++){let i=e[`cScale${a}`];r+=`
		.radarCurve-${a} {
			color: ${i};
			fill: ${i};
			fill-opacity: ${t.curveOpacity};
			stroke: ${i};
			stroke-width: ${t.curveStrokeWidth};
		}
		.radarLegendBox-${a} {
			fill: ${i};
			fill-opacity: ${t.curveOpacity};
			stroke: ${i};
		}
		`}return r},"genIndexStyles"),it=l(e=>{let t=E(),r=w(),a=v(t,r.themeVariables),i=v(a.radar,e);return{themeVariables:a,radarOptions:i}},"buildRadarStyleOptions"),ot={parser:Q,db:$,renderer:et,styles:l(({radar:e}={})=>{let{themeVariables:t,radarOptions:r}=it(e);return`
	.radarTitle {
		font-size: ${t.fontSize};
		color: ${t.titleColor};
		dominant-baseline: hanging;
		text-anchor: middle;
	}
	.radarAxisLine {
		stroke: ${r.axisColor};
		stroke-width: ${r.axisStrokeWidth};
	}
	.radarAxisLabel {
		dominant-baseline: middle;
		text-anchor: middle;
		font-size: ${r.axisLabelFontSize}px;
		color: ${r.axisColor};
	}
	.radarGraticule {
		fill: ${r.graticuleColor};
		fill-opacity: ${r.graticuleOpacity};
		stroke: ${r.graticuleColor};
		stroke-width: ${r.graticuleStrokeWidth};
	}
	.radarLegendText {
		text-anchor: start;
		font-size: ${r.legendFontSize}px;
		dominant-baseline: hanging;
	}
	${at(t,r)}
	`},"styles")};export{ot as diagram};
